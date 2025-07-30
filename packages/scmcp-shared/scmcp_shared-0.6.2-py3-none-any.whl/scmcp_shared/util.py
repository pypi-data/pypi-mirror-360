import inspect
import os
from pathlib import Path
from fastmcp.server.dependencies import get_context
from fastmcp.exceptions import ToolError
import asyncio
import nest_asyncio
from pydantic import BaseModel


def get_env(key):
    return os.environ.get(f"SCMCP_{key.upper()}")


def filter_args(request, func, **extra_kwargs):
    kwargs = request.model_dump()
    args = request.model_fields_set
    parameters = inspect.signature(func).parameters
    extra_kwargs = {k: extra_kwargs[k] for k in extra_kwargs if k in parameters}
    func_kwargs = {k: kwargs.get(k) for k in args if k in parameters}
    func_kwargs.update(extra_kwargs)
    return func_kwargs


def add_op_log(adata, func, kwargs, adinfo):
    import hashlib
    import json

    if "operation" not in adata.uns:
        adata.uns["operation"] = {}
        adata.uns["operation"]["op"] = {}
        adata.uns["operation"]["opid"] = []
    # Handle different function types to get the function name
    if hasattr(func, "func") and hasattr(func.func, "__name__"):
        # For partial functions, use the original function name
        func_name = func.func.__name__
    elif hasattr(func, "__name__"):
        func_name = func.__name__
    elif hasattr(func, "__class__"):
        func_name = func.__class__.__name__
    else:
        func_name = str(func)
    new_kwargs = {**adinfo.model_dump()}
    for k, v in kwargs.items():
        if isinstance(v, tuple):
            new_kwargs[k] = list(v)
        else:
            new_kwargs[k] = v
    try:
        kwargs_str = json.dumps(new_kwargs, sort_keys=True)
    except Exception as e:
        print(e)
        kwargs_str = f"{e}" + str(new_kwargs)
    hash_input = f"{func_name}:{kwargs_str}"
    hash_key = hashlib.md5(hash_input.encode()).hexdigest()
    adata.uns["operation"]["op"][hash_key] = {func_name: new_kwargs}
    adata.uns["operation"]["opid"] = list(adata.uns["operation"]["opid"])
    adata.uns["operation"]["opid"].append(hash_key)
    from .logging_config import setup_logger

    logger = setup_logger(log_file=get_env("LOG_FILE"))
    logger.info(f"{func}: {new_kwargs}")


def save_fig_path(axes, file):
    from matplotlib.axes import Axes

    try:
        file_path = Path(file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(axes, list):
            if isinstance(axes[0], Axes):
                axes[0].figure.savefig(file_path)
        elif isinstance(axes, dict):
            ax = list(axes.values())[0]
            if isinstance(ax, Axes):
                ax.figure.savefig(file_path)
        elif isinstance(axes, Axes):
            axes.figure.savefig(file_path)
        elif hasattr(axes, "savefig"):  # if Figure
            axes.savefig(file_path)
        elif hasattr(axes, "save"):  # for plotnine.ggplot.ggplot
            axes.save(file_path)
        else:
            raise ValueError(
                f"axes must be a Axes or plotnine object, but got {type(axes)}"
            )
        return file_path
    except Exception as e:
        raise e


def savefig(axes, func=None, **kwargs):
    if hasattr(func, "func") and hasattr(func.func, "__name__"):
        # For partial functions, use the original function name
        func_name = func.func.__name__
    elif hasattr(func, "__name__"):
        func_name = func.__name__
    elif hasattr(func, "__class__"):
        func_name = func.__class__.__name__
    else:
        func_name = str(func)

    fig_dir = Path(os.getcwd()) / "figures"
    kwargs.pop("save", None)
    kwargs.pop("show", None)
    args = []
    for k, v in kwargs.items():
        if isinstance(v, (tuple, list, set)):
            v = v[:3]  ## show first 3 elements
            args.append(f"{k}-{'-'.join([str(i) for i in v])}")
        elif isinstance(v, dict):
            v = list(v.keys())[:3]  ## show first 3 elements
            args.append(f"{k}-{'-'.join([str(i) for i in v])}")
        else:
            args.append(f"{k}-{v}")
    args_str = "_".join(args).replace(" ", "")
    fig_path = fig_dir / f"{func_name}_{args_str}.png"
    try:
        save_fig_path(axes, fig_path)
    except PermissionError:
        raise PermissionError("You don't have permission to save figure")
    except Exception as e:
        raise e
    transport = get_env("TRANSPORT")
    if transport == "stdio":
        return fig_path
    else:
        host = get_env("HOST")
        port = get_env("PORT")
        fig_path = f"http://{host}:{port}/figures/{Path(fig_path).name}"
        return fig_path


async def get_figure(request):
    from starlette.responses import FileResponse, Response

    figure_name = request.path_params["figure_name"]
    figure_path = f"./figures/{figure_name}"

    if not os.path.isfile(figure_path):
        return Response(
            content={"error": "figure not found"}, media_type="application/json"
        )

    return FileResponse(figure_path)


def add_figure_route(server):
    from starlette.routing import Route

    server._additional_http_routes = [
        Route("/figures/{figure_name}", endpoint=get_figure)
    ]


async def async_forward_request(func, request, adinfo, **kwargs):
    from fastmcp import Client

    forward_url = get_env("FORWARD")
    request_kwargs = request.model_dump()
    request_args = request.model_fields_set
    func_kwargs = {
        "request": {k: request_kwargs.get(k) for k in request_args},
        "adinfo": adinfo.model_dump(),
    }
    if not forward_url:
        return None

    client = Client(forward_url)
    async with client:
        tools = await client.list_tools()
        func = [t.name for t in tools if t.name.endswith(func)][0]
        try:
            result = await client.call_tool(func, func_kwargs)
            return result
        except ToolError as e:
            raise ToolError(e)
        except Exception as e:
            if hasattr(e, "__context__") and e.__context__:
                raise Exception(f"{str(e.__context__)}")
            else:
                raise e


def forward_request(func, request, adinfo, **kwargs):
    """Synchronous wrapper for forward_request"""
    try:
        # Apply nest_asyncio to allow nested event loops
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in a running event loop, use create_task
            async def _run():
                return await async_forward_request(func, request, adinfo, **kwargs)

            return loop.run_until_complete(_run())
        else:
            # If no event loop is running, use asyncio.run()
            return asyncio.run(async_forward_request(func, request, adinfo, **kwargs))
    except Exception as e:
        if hasattr(e, "__context__") and e.__context__:
            raise Exception(f"{str(e.__context__)}")
        else:
            raise e


def obsm2adata(adata, obsm_key):
    from anndata import AnnData

    if obsm_key not in adata.obsm_keys():
        raise ValueError(f"key {obsm_key} not found in adata.obsm")
    else:
        return AnnData(
            adata.obsm[obsm_key], obs=adata.obs, obsm=adata.obsm, uns=adata.uns
        )


def get_ads():
    ctx = get_context()
    ads = ctx.request_context.lifespan_context
    return ads


def generate_msg(adinfo, adata, ads):
    return {
        "sampleid": adinfo.sampleid or ads.active_id,
        "adtype": adinfo.adtype,
        "adata": adata,
    }


def sc_like_plot(plot_func, adata, request, adinfo, **kwargs):
    from matplotlib import pyplot as plt

    func_kwargs = filter_args(request, plot_func, show=False, save=False)
    axes = plot_func(adata, **func_kwargs)
    if axes is None:
        axes = plt.gca()
    fig_path = savefig(axes, plot_func, **func_kwargs)
    add_op_log(adata, plot_func, func_kwargs, adinfo)
    return fig_path


def filter_tools(mcp, include_tools=None, exclude_tools=None):
    import asyncio
    import copy

    mcp = copy.deepcopy(mcp)

    async def _filter_tools(mcp, include_tools=None, exclude_tools=None):
        tools = await mcp.get_tools()
        for tool in tools:
            if exclude_tools and tool in exclude_tools:
                mcp.remove_tool(tool)
            if include_tools and tool not in include_tools:
                mcp.remove_tool(tool)
        return mcp

    return asyncio.run(_filter_tools(mcp, include_tools, exclude_tools))


def set_env(log_file, forward, transport, host, port):
    if log_file is not None:
        os.environ["SCMCP_LOG_FILE"] = log_file
    if forward is not None:
        os.environ["SCMCP_FORWARD"] = forward
    os.environ["SCMCP_TRANSPORT"] = transport
    os.environ["SCMCP_HOST"] = host
    os.environ["SCMCP_PORT"] = str(port)


def setup_mcp(mcp, sub_mcp_dic, modules=None):
    import asyncio

    if modules is None or modules == "all":
        modules = sub_mcp_dic.keys()
    for module in modules:
        asyncio.run(mcp.import_server(module, sub_mcp_dic[module]))
    return mcp


def _update_args(mcp, func, args_dic: dict):
    for args, property_dic in args_dic.items():
        for pk, v in property_dic.items():
            mcp._tool_manager._tools[func].parameters["properties"][
                "request"
            ].setdefault(pk, {})
            mcp._tool_manager._tools[func].parameters["properties"]["request"][pk][
                args
            ] = v


def update_mcp_args(mcp, tool_args: dict):
    # tools = mcp._tool_manager._tools.keys()
    for tool in tool_args:
        _update_args(mcp, tool, tool_args[tool])


def check_adata(adata, adinfo, ads):
    sampleid = adinfo.sampleid or ads.active_id
    if sampleid != adata.uns["scmcp_sampleid"]:
        raise ValueError(
            f"sampleid mismatch: {sampleid} != {adata.uns['scmcp_sampleid']}"
        )


def get_nbm():
    ctx = get_context()
    nbm = ctx.request_context.lifespan_context
    return nbm


def parse_args(
    kwargs: BaseModel | dict,
    positional_args: list[str] | str | None = None,
    func_args: list[str] | str | None = None,
) -> str:
    if isinstance(kwargs, BaseModel):
        kwargs = kwargs.model_dump()
    elif isinstance(kwargs, dict):
        kwargs = kwargs
    else:
        raise ValueError(f"Invalid type: {type(kwargs)}")

    if func_args is not None:
        if isinstance(func_args, str):
            func_args = [func_args]
    else:
        func_args = []
    kwargs_str_ls = []
    if positional_args is not None:
        if isinstance(positional_args, str):
            kwargs_str_ls.append(kwargs.pop(positional_args))
        elif isinstance(positional_args, list):
            for arg in positional_args:
                kwargs_str_ls.append(kwargs.pop(arg))

    extra_kwargs = kwargs.pop("kwargs", {})
    for k, v in kwargs.items():
        if k in func_args:
            kwargs_str_ls.append(f"{k}={v}")
            continue
        if isinstance(v, (list, tuple, dict, int, float, bool)):
            kwargs_str_ls.append(f"{k}={v}")
        elif isinstance(v, str):
            kwargs_str_ls.append(f"{k}='{v}'")

    if extra_kwargs:
        kwargs_str_ls.append(f"**{extra_kwargs}")

    kwargs_str = ", ".join(kwargs_str_ls)
    return kwargs_str
