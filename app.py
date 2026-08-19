from __future__ import annotations

import streamlit as st

from src.logging_config import configure_logging
from src.runtime import create_runtime
from src.ui import render


def main() -> None:
    st.set_page_config(
        page_title="InsightSQL",
        page_icon="▦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    configure_logging()
    render(create_runtime())


if __name__ == "__main__":
    main()
