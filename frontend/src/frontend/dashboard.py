import streamlit as st
import httpx
import pandas as pd
import os


def get_backend_url() -> str:
    backend_url = os.getenv("BACKEND_URL", "").strip()
    if not backend_url:
        try:
            backend_url = str(st.secrets.get("BACKEND_URL", "")).strip()
        except (FileNotFoundError, KeyError):
            backend_url = ""

    if not backend_url:
        backend_url = "https://pokemon-backend-frug.onrender.com"

    return backend_url.rstrip("/")


def main():
    base_url = get_backend_url()
    st.markdown("# PokeHub")

    st.write(base_url)

    stats = httpx.get(f"{base_url}/pokemon/stats").json()

    st.markdown("All cool stuff you'll need to know about these cute little monsters!!!")

    st.markdown("## PokeTypes")
    pokemons_per_type = httpx.get(f"{base_url}/pokemon/number_types").json()

    pokemons_per_type = pd.DataFrame(
        list(pokemons_per_type.items()), columns=["type", "number"],
    )
    st.bar_chart(pokemons_per_type.head(8), x="type", y="number")

    st.dataframe(stats)

    df = pd.DataFrame(stats)
    types = df["Type 1"].unique()
    poke_type = st.selectbox(label="Choose pokemon type", options=types)

    poke_types = httpx.get(f"{base_url}/pokemons/type", params={"poke_type": poke_type}).json()

    st.dataframe(poke_types)

    st.markdown("Pokemon stats")

if __name__ == "__main__":
    main()