# Financial Calc BR 🇧🇷

[](https://www.google.com/search?q=https://pypi.org/project/financial-calc-br/)
[](https://opensource.org/licenses/MIT)

Uma calculadora financeira completa para o mercado brasileiro, incluindo cálculos de financiamentos (SAC e Price), investimentos (CDB, Tesouro Selic, Poupança) e cartão de crédito rotativo.

## 📦 Instalação

### pip

```bash
pip install financial-calc-br
```

## 🚀 Uso Básico

### Calculadora de Financiamentos

```python
from financial_calc_br import FinancingCalc

calc = FinancingCalc()

# Calcular financiamento SAC
sac = calc.financing_sac(300000, 10.5, 30)
print(sac.formatted.primeira_parcela)

# Calcular financiamento Price
price = calc.financing_price(300000, 10.5, 30)
print(price.formatted.prestacao_fixa)

# Comparar os dois sistemas
comparison = calc.compare_financing(300000, 10.5, 30)
print(comparison.comparison.recommendation)
```

### Calculadora de Investimentos

```python
from financial_calc_br import InvestmentCalc

calc = InvestmentCalc()

# Calcular rendimento da poupança
poupanca = calc.investment_poupanca(10000, 12)
print(poupanca.formatted.rendimento)

# Calcular CDB
# 110% do CDI
cdb = calc.investment_cdb(10000, 12, 110)
print(cdb.formatted.rendimento_liquido)

# Comparar investimentos
comparison = calc.compare_investments(10000, 12)
print(comparison.best_option.name)
```

### Calculadora de Cartão de Crédito

```python
from financial_calc_br import CreditCardCalc

calc = CreditCardCalc()

# Calcular rotativo do cartão
# Fatura R$ 1000, pagou R$ 300, taxa 15%
rotativo = calc.calc_revolving(1000, 300, 15)
print(rotativo.formatted.custo_total)
print(rotativo.alert)
```

## 📊 Funcionalidades

### 🏠 Financiamentos

  - **Sistema SAC**: Parcelas decrescentes, menor custo total.
  - **Sistema Price**: Parcelas fixas, facilita o planejamento.
  - **Comparação**: Análise automática de ambos os sistemas.
  - **Simulação de Entrada**: Calcule diferentes cenários de entrada.

### 💰 Investimentos

  - **Poupança**: Cálculo com as regras atuais (isento de IR).
  - **Tesouro Selic**: Com tributação regressiva.
  - **CDB**: Diversos percentuais do CDI.
  - **Aportes Mensais**: Simulação de investimentos recorrentes.
  - **Taxas Atualizadas**: Busca automática das taxas Selic e CDI.

### 💳 Cartão de Crédito

  - **Rotativo**: Cálculo de juros e IOF.
  - **Alertas**: Identifica custos altos automaticamente.
  - **Próxima Fatura**: Projeção do valor da próxima fatura.

## 🛠️ API Completa

### FinancingCalc

```python
# Financiamento SAC
def financing_sac(self, valor: float, taxa_anual: float, anos: float) -> ResultadoSAC:

# Financiamento Price
def financing_price(self, valor: float, taxa_anual: float, anos: float) -> ResultadoPRICE:

# Comparar sistemas
def compare_financing(self, valor: float, taxa_anual: float, anos: float) -> ResultadoComparacao:

# Simular entrada
def simulate_down_payment(self, valor_imovel: float, entrada: float, taxa_anual: float, anos: float) -> SimulacaoEntrada:
```

### InvestmentCalc

```python
# Poupança
def investment_poupanca(self, valor: float, meses: float) -> ResultadoPoupanca:

# Tesouro Selic
def investment_tesouro_selic(self, valor: float, meses: float) -> ResultadoTesouroSelic:

# CDB
def investment_cdb(self, valor: float, meses: float, percentual_cdi: float) -> ResultadoCDB:

# Comparar investimentos
def compare_investments(self, valor: float, meses: float, opcoes: list = None) -> ResultadoComparacaoInvestment:

# Aportes mensais
def simulate_monthly_contributions(self, valor_inicial: float, aporte_mensal: float, meses: float, taxa_anual: float, tem_ir: bool = False) -> SimulacaoAportes:
```

### CreditCardCalc

```python
# Rotativo do cartão
def calc_revolving(self, valor_fatura: float, valor_pago: float, taxa_mensal: float = None) -> (creditCard, creditCardPaga):
```

### RatesManager

```python
# Buscar taxas atualizadas (método)
def update_all(self) -> Rates:

# Taxas individuais (atributos de classe)
selic: float
cdi: float
poupanca: float
dolar: float
ipca: float

# Obter todas as taxas (método)
def get_all_rates(self) -> AllRates:
```

## 🔧 Utilitários

```python
from financial_calc_br import format_money, parse_money, convert_rate, calc_ir_rate

# Formatação
format_money(1234.56)
parse_money("R$ 1.234,56")

# Conversão de taxas
convert_rate(12, "annual", "monthly")
convert_rate(1, "monthly", "annual")

# Cálculo de IR
calc_ir_rate(90)
calc_ir_rate(400)
```

## 📈 Exemplos Práticos

### Comparando Financiamento de R$ 500.000

```python
from financial_calc_br import FinancingCalc

calc = FinancingCalc()
result = calc.compare_financing(500000, 11.5, 30)

print(f"SAC - Primeira parcela: {result.sac.primeira}")
print(f"Price - Parcela fixa: {result.price.parcela_fixa}")
print(f"Economia escolhendo SAC: {result.comparison.formatted.economia}")
print(f"Recomendação: {result.comparison.recommendation.system}")
```

### Simulando Investimento com Aportes

```python
from financial_calc_br import InvestmentCalc

calc = InvestmentCalc()
simulation = calc.simulate_monthly_contributions(10000, 1000, 24, 12)

print(f"Total aportado: {simulation.formatted.total_aportado}")
print(f"Rendimento líquido: {simulation.formatted.rendimento_liquido}")
print(f"Montante final: {simulation.formatted.montante_liquido}")
```

## 🇧🇷 Específico para o Brasil

  - **Taxas Reais**: Integração com APIs do Banco Central.
  - **Tributação Brasileira**: IR progressivo e regressivo.
  - **Regras da Poupança**: Aplicação automática das regras atuais.
  - **Formatação**: Valores em Real (R$) e períodos em português.
  - **IOF**: Cálculo automático para cartão de crédito.

## Existe também está mesma biblioteca para o npm 📦:
  - **repositorio para utilizar no npm**: https://github.com/raulcabralc/financial-calc-br

## 📝 Licença

MIT © [Raul Cabral](https://github.com/raulcabralc) [Lucas Andrade](https://github.com/lucansdev)

## 🤝 Contribuindo

Contribuições são bem-vindas\! Veja [CONTRIBUTING.md](https://www.google.com/search?q=CONTRIBUTING.md) para detalhes.

## 🐛 Bugs e Sugestões

Encontrou um bug ou tem uma sugestão? Abra uma [issue](https://github.com/lucansdev/financial-calc-br/issues).

## 📊 Roadmap

  - [ ] Calculadora de aposentadoria
  - [ ] Simulador de empréstimos
  - [ ] Calculadora de impostos
  - [ ] Integração com mais APIs financeiras
  - [ ] Dashboard web interativo
