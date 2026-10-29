from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class AnalisadorDeVendas:
    """Limpa, transforma e analisa dados de vendas."""

    def __init__(self, arquivo_csv):
        self.arquivo_csv = Path(arquivo_csv)
        self.df_bruto = None
        self.df_vendas = None

    def carregar_dados(self):
        self.df_bruto = pd.read_csv(self.arquivo_csv)
        return self.df_bruto

    def limpar_dados(self):
        if self.df_bruto is None:
            self.carregar_dados()

        df = self.df_bruto.copy()

        df["data_venda"] = pd.to_datetime(
            df["data_venda"],
            format="%Y-%m-%d",
            errors="coerce"
        )
        df["quantidade"] = pd.to_numeric(
            df["quantidade"], errors="coerce"
        )
        df["preco_unitario"] = pd.to_numeric(
            df["preco_unitario"], errors="coerce"
        )

        df = df.dropna(
            subset=[
                "data_venda", "cliente", "produto",
                "categoria", "regiao", "quantidade",
                "preco_unitario"
            ]
        )

        df = df[
            (df["quantidade"] > 0)
            & (df["preco_unitario"] >= 0)
        ].copy()

        df["id_venda"] = pd.to_numeric(
            df["id_venda"], errors="coerce"
        )
        df = df.dropna(subset=["id_venda"])
        df["id_venda"] = df["id_venda"].astype(int)

        self.df_vendas = df
        return df

    def transformar_dados(self):
        if self.df_vendas is None:
            self.limpar_dados()

        df = self.df_vendas.copy()
        df["receita"] = (
            df["quantidade"] * df["preco_unitario"]
        ).round(2)
        df["ano"] = df["data_venda"].dt.year
        df["mes"] = df["data_venda"].dt.month
        df["trimestre"] = df["data_venda"].dt.quarter

        df["faixa_receita"] = np.select(
            [
                df["receita"] < 500,
                df["receita"].between(
                    500, 2000, inclusive="left"
                ),
                df["receita"] >= 2000
            ],
            ["Baixa", "Media", "Alta"],
            default="Indefinida"
        )

        self.df_vendas = df
        return df

    def analisar_vendas(self):
        if self.df_vendas is None or "receita" not in self.df_vendas:
            self.transformar_dados()

        df = self.df_vendas

        return {
            "mes": (
                df.groupby(["ano", "mes"], as_index=False)
                .agg(
                    receita_total=("receita", "sum"),
                    quantidade_vendida=("quantidade", "sum"),
                    numero_vendas=("id_venda", "count")
                )
                .sort_values(["ano", "mes"])
            ),
            "produto": (
                df.groupby("produto", as_index=False)
                .agg(
                    receita_total=("receita", "sum"),
                    quantidade_vendida=("quantidade", "sum")
                )
                .sort_values("receita_total", ascending=False)
            ),
            "categoria": (
                df.groupby("categoria", as_index=False)
                .agg(
                    receita_total=("receita", "sum"),
                    quantidade_vendida=("quantidade", "sum")
                )
                .sort_values("receita_total", ascending=False)
            ),
            "regiao": (
                df.groupby("regiao", as_index=False)
                .agg(
                    receita_total=("receita", "sum"),
                    numero_vendas=("id_venda", "count")
                )
                .sort_values("receita_total", ascending=False)
            )
        }

    def segmentar_clientes(self):
        df = self.df_vendas

        clientes = (
            df.groupby("cliente", as_index=False)
            .agg(gasto_total=("receita", "sum"))
        )

        clientes["segmento"] = clientes["gasto_total"].apply(
            lambda valor: (
                "Bronze" if valor < 10000
                else "Prata" if valor < 30000
                else "Ouro"
            )
        )

        return clientes.sort_values(
            "gasto_total", ascending=False
        )


    def gerar_graficos(self, pasta_saida):
        """Gera e salva quatro gráficos de análise."""
        pasta_saida = Path(pasta_saida)
        pasta_saida.mkdir(parents=True, exist_ok=True)

        df = self.df_vendas

        # 1. Receita mensal
        mensal = (
            df.groupby(["ano", "mes"])["receita"]
            .sum()
            .reset_index()
            .sort_values(["ano", "mes"])
        )
        mensal["periodo"] = (
            mensal["ano"].astype(str) + "-"
            + mensal["mes"].astype(str).str.zfill(2)
        )

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(
            data=mensal, x="periodo", y="receita",
            marker="o", ax=ax
        )
        ax.set_title("Receita mensal de vendas")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Receita (R$)")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        fig.savefig(pasta_saida / "receita_por_mes.png", dpi=150)
        plt.close(fig)

        # 2. Cinco produtos com maior receita
        produtos = (
            df.groupby("produto")["receita"]
            .sum().nlargest(5).reset_index()
        )
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(
            data=produtos, x="receita", y="produto", ax=ax
        )
        ax.set_title("Top 5 produtos por receita")
        ax.set_xlabel("Receita (R$)")
        ax.set_ylabel("Produto")
        fig.tight_layout()
        fig.savefig(pasta_saida / "top_produtos.png", dpi=150)
        plt.close(fig)

        # 3. Quantidade versus receita
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(
            data=df, x="quantidade", y="receita",
            hue="categoria", alpha=0.75, ax=ax
        )
        ax.set_title("Quantidade vendida versus receita")
        ax.set_xlabel("Quantidade")
        ax.set_ylabel("Receita por transação (R$)")
        fig.tight_layout()
        fig.savefig(
            pasta_saida / "quantidade_vs_receita.png", dpi=150
        )
        plt.close(fig)

        # 4. Painel com quatro visualizações
        fig, axes = plt.subplots(2, 2, figsize=(14, 9))

        sns.lineplot(
            data=mensal, x="periodo", y="receita",
            marker="o", ax=axes[0, 0]
        )
        axes[0, 0].set_title("Receita mensal")
        axes[0, 0].tick_params(axis="x", rotation=45)

        categorias = (
            df.groupby("categoria")["receita"]
            .sum().reset_index()
        )
        sns.barplot(
            data=categorias, x="categoria", y="receita",
            ax=axes[0, 1]
        )
        axes[0, 1].set_title("Receita por categoria")
        axes[0, 1].tick_params(axis="x", rotation=20)

        sns.histplot(
            data=df, x="receita", bins=20, ax=axes[1, 0]
        )
        axes[1, 0].set_title("Distribuição da receita por venda")

        regioes = (
            df.groupby("regiao")["quantidade"]
            .sum().reset_index()
            .sort_values("quantidade", ascending=False)
        )
        sns.barplot(
            data=regioes, x="regiao", y="quantidade",
            ax=axes[1, 1]
        )
        axes[1, 1].set_title("Quantidade por região")
        axes[1, 1].tick_params(axis="x", rotation=25)

        fig.suptitle("SalesInsight PY | Painel de Vendas")
        fig.tight_layout()
        fig.savefig(pasta_saida / "painel_resumo.png", dpi=150)
        plt.close(fig)

        print("Quatro gráficos gerados em:", pasta_saida)

    def exportar_resultados(self, resultados, pasta_saida):
        pasta_saida = Path(pasta_saida)
        pasta_saida.mkdir(parents=True, exist_ok=True)

        resultados["mes"].to_csv(
            pasta_saida / "metricas_por_mes.csv",
            index=False
        )

        resultados["produto"].to_csv(
            pasta_saida / "metricas_por_produto.csv",
            index=False
        )

        resultados["categoria"].to_csv(
            pasta_saida / "metricas_por_categoria.csv",
            index=False
        )

        resultados["regiao"].to_csv(
            pasta_saida / "metricas_por_regiao.csv",
            index=False
        )

        clientes = self.segmentar_clientes()
        clientes.to_csv(
            pasta_saida / "segmentacao_clientes.csv",
            index=False
        )

        df = self.df_vendas

        estatisticas = {
            "total_vendas": int(len(df)),
            "receita_total": round(float(df["receita"].sum()), 2),
            "quantidade_total": int(df["quantidade"].sum()),
            "ticket_medio": round(float(df["receita"].mean()), 2),
            "total_clientes": int(df["cliente"].nunique())
        }

        with open(
            pasta_saida / "estatisticas_gerais.json",
            "w",
            encoding="utf-8"
        ) as arquivo:
            json.dump(
                estatisticas, arquivo,
                ensure_ascii=False, indent=4
            )

        return estatisticas


def main():
    raiz = Path(__file__).resolve().parent
    arquivo_csv = raiz / "vendas.csv"
    pasta_saida = raiz / "outputs"

    analisador = AnalisadorDeVendas(arquivo_csv)
    analisador.carregar_dados()
    analisador.limpar_dados()
    analisador.transformar_dados()

    resultados = analisador.analisar_vendas()
    estatisticas = analisador.exportar_resultados(
        resultados, pasta_saida
    )
    analisador.gerar_graficos(pasta_saida / "graficos")

    print("Análise concluída!")
    print(json.dumps(estatisticas, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
