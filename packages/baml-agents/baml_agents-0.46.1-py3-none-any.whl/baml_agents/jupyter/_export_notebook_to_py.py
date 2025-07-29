def export_notebook_to_py(target_folder: str = "notebook_py_exports") -> None:
    """
    Exports marked cells from the current Jupyter Notebook to .py files
    within the specified target_folder.

    At the top of the notebook
    # | default_exp s02

    Each cell that you want to export should start with:
    # | export

    Note: All imports should be in a separate # | export cell.

    Call this function from within a notebook, at the end of your notebook.

    Read more: https://nbdev.fast.ai/
    """
    import IPython

    current_notebook_path = IPython.get_ipython().user_ns["__vsc_ipynb_file__"]  # type: ignore
    from nbdev.export import nb_export  # type: ignore

    nb_export(
        nbname=current_notebook_path,
        lib_path=target_folder,
    )
    try:
        from loguru import logger
    except ImportError:
        import logging

        logger = logging.getLogger(__name__)

    msg = f"Successfully exported notebook to: {target_folder}"
    logger.info(msg)
