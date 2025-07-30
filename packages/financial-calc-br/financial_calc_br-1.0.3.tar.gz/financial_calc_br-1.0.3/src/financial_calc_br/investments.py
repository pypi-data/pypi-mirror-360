from utils import parseMoney,convertRate,calcIRRate,validateFinancialParams,formatPeriod,formatMoney
import math
from rates import RatesManager
import datetime

class InvestmentCalc:
    def __init__(self) -> None:
        self.rates = RatesManager()

    def investmentPoupanca(self,valor:float,meses:float):
        validation = validateFinancialParams(valor,self.rates.poupanca,meses)

        if not validation.get("isValid"):
            erros_str = ",".join(validation.get("errors"))
            raise ValueError(f"Parâmetros inválidos :{erros_str}")
        
        taxaMensal:float = self.rates.poupanca / 100
        montante:float = valor * math.pow(1 + taxaMensal,meses)
        rendimento:float = montante - valor

        return{
            "investimento":"Poupanca",
            "valorInicial":valor,
            "periodo":meses,
            "taxaMensal":self.rates.poupanca / 100,
            "montanteFinal":montante,
            "rendimento":rendimento,
            "rentabilidade":rendimento / valor,
            "isento":True,
            "observacao":"Isento de Imposto de Renda e IOF",
            "formatted":{
                "valorInicial":formatMoney(valor),
                "periodo":formatPeriod(meses),
                "taxaMensal":f"{self.rates.poupanca:.2f}%",
                "montanteFinal":formatMoney(montante),
                "rendimento":formatMoney(rendimento),
                "rentabilidade":f"{((rendimento/valor) * 100):.2f}% "
            }
        }
    def investmentTesouroSelic(self,valor:float,meses:float):
        validation = validateFinancialParams(valor,
                                             self.rates.selic,
                                             meses)
        
        if not validation.get("isValid"):
            erros_str = ",".join(validation.get("errors"))
            raise ValueError(f"Parâmetros inválidos :{erros_str}")
        
        taxaMensal:float = convertRate(self.rates.selic,"anual","mensal") / 100
        montanteBruto:float = valor * math.pow(1 + taxaMensal,meses)
        rendimentoBruto:float = montanteBruto - valor

        dias:float = meses*30
        aliquotaIR:float = calcIRRate(dias)
        ir:float = rendimentoBruto * (aliquotaIR / 100)
        rendimentoLiquido:float = rendimentoBruto - ir

        return {
            "investimento":"Tesouro Selic",
            "valorInicial":valor,
            "periodo":meses,
            "taxaAnual":self.rates.selic / 100,
            "montanteBruto":montanteBruto,
            "impostoRenda":ir,
            "aliquotaIR":aliquotaIR/100,
            "montanteLiquido":valor + rendimentoLiquido,
            "rendimentoLiquido":rendimentoLiquido,
            "rentabilidade":rendimentoLiquido / valor,
            "observacao":f"Tributação regressiva: {aliquotaIR}% de IR após {math.floor(dias)} dias",
            "formatted":{
                "valorInicial":formatMoney(valor),
                "periodo":formatPeriod(meses),
                "taxaAnual":f"{self.rates.selic}%",
                "montanteBruto":formatMoney(montanteBruto),
                "impostoRenda":formatMoney(ir),
                "aliquotaIR":f"{aliquotaIR}%",
                "montanteLiquido":formatMoney(valor + rendimentoLiquido),
                "rendimentoLiquido":formatMoney(rendimentoLiquido),
                "rentabilidade":f"{((rendimentoLiquido/valor)*100):.2f}%"
            }
        }

    def investmentCDB(self,valor:float,meses:float,percentualCDI:float= 100):
        validation = validateFinancialParams(valor,percentualCDI,meses)

        if not validation.get("isValid"):
            erros_str = ",".join(validation.get("errors"))
            raise ValueError(f"Parâmetros inválidos :{erros_str}")

        taxaCDI:float = self.rates.cdi * (percentualCDI / 100)
        taxaMensal:float = convertRate(taxaCDI,"anual","mensal") / 100
        montanteBruto:float = valor * math.pow(1 + taxaMensal,meses)
        rendimentoBruto:float = montanteBruto - valor 

        dias:float = meses * 30
        aliquotaIR:float = calcIRRate(dias)
        ir:float = rendimentoBruto * (aliquotaIR / 100)
        rendimentoLiquido:float = rendimentoBruto - ir

        return{
            "investimento":f"CDB {percentualCDI}% CDI",
            "valorInicial":valor,
            "periodo":meses,
            "taxaAnual":taxaCDI / 100,
            "percentualCDI": percentualCDI / 100,
            "montanteBruto":montanteBruto,
            "impostoRenda":ir,
            "aliquotaIR":aliquotaIR / 100,
            "montanteLiquido":valor + rendimentoLiquido,
            "rendimentoLiquido":rendimentoLiquido,
            "rentabilidade":rendimentoLiquido / valor,
            "formatted":{
                "valorInicial":formatMoney(valor),
                "periodo":formatPeriod(meses),
                "taxaAnual":f"{taxaCDI:.2f}%",
                "percentualCDI":f"{percentualCDI}%",
                "montanteBruto":formatMoney(montanteBruto),
                "impostoRenda":formatMoney(ir),
                "aliquotaIR":f"{aliquotaIR}%",
                "montanteLiquido":formatMoney(valor + rendimentoLiquido),
                "rendimentoLiquido":formatMoney(rendimentoLiquido),
                "rentabilidade":f"{((rendimentoLiquido/valor) * 100):.2f}%"
            }
        }
    
    def compareInvestments(self,valor:float,meses:float,opcoes:list = [100,110,120]):
        poupanca = self.investmentPoupanca(valor,meses)
        selic = self.investmentTesouroSelic(valor,meses)

        cdbs:list = [self.investmentCDB(valor,meses,perc) for perc in opcoes]

        rendPoupanca:float = parseMoney(poupanca.get("rendimento"))
        rendSelic:float = parseMoney(selic.get("rendimentoLiquido"))

        rendCDBs:list = [{
            "nome":cdb["investimento"],
            "rendimento":parseMoney(cdb["rendimentoLiquido"]),
            "rentabilidade":cdb["rentabilidade"]
        }for cdb in cdbs]

        todasOpcoes:list = [{
            "nome":"Poupança",
            "rendimento":rendPoupanca,
            "rentabilidade":poupanca.get("rentabilidade")
        },
        {
            "nome":"Tesouro Selic",
            "rendimento":rendSelic,
            "rentabilidade":selic.get("rentabilidade")
        },
        ]

        melhorOpcao = max(todasOpcoes, key=lambda opcao: opcao["rendimento"])


        return {
            "cenario":{
                "valor":valor,
                "periodo":formatPeriod(meses),
                "dataAnalise":datetime.date.today().strftime("%d/%m/%Y")
            },
            "opcoes":{
                "poupanca":{
                    "rendimento":poupanca.get("rendimento"),
                    "rentabilidade":poupanca.get("rentabilidade")
                },
                "tesouroSelic":{
                    "rendimento":selic.get("rendimentoLiquido"),
                    "rentabilidade":selic.get("rentabilidade")
                },
                "cdbs":[{
                    "nome":cdb["investimento"],
                    "rendimento":cdb["rendimentoLiquido"],
                    "rentabilidade":cdb["rentabilidade"]

                }for cdb in cdbs]
            },
            "ranking": sorted(todasOpcoes,key=lambda opcao:opcao["rendimento"]),
            "melhorOpcao":{
                "nome":melhorOpcao.get("nome"),
                "rendimento":melhorOpcao.get("rendimento"),
                "rentabilidade":melhorOpcao.get("rentabilidade"),
                "vantagem":melhorOpcao.get("rendimento") - min([option.get("rendimento") for option in todasOpcoes])

            },
            "taxasUtilizadas":{
                "selic":self.rates.getAllRates().get("formatted").get("selic"),
                "cdi":self.rates.getAllRates().get("formatted").get("poupanca"),
                "poupanca":self.rates.getAllRates().get("formatted").get("poupanca"),
                "atualizadoEm":datetime.date.today().strftime("%d/%m/%Y")
            }

        }
    

    def simulateMonthlyContribution(valorInicial:float,aporteMensal:float,meses:float,taxaAnual:float,temIR:bool=True):
        validation = validateFinancialParams(valorInicial,taxaAnual,meses)

        if not validation.get("isValid"):
            erros_str = ",".join(validation.get("errors"))
            raise ValueError(f"Parâmetros inválidos :{erros_str}")
        
        taxaMensal:float = convertRate(taxaAnual,"anual","mensal") / 100
        montante:float = valorInicial
        totalAportado:float = valorInicial
        evolucao:list = []


        for mes in range(1,meses + 1):
            montante = montante * (1 + taxaMensal)

            if mes <= meses:
                montante += aporteMensal
                totalAportado += aporteMensal


            if mes <= 12 or mes % 12 ==0 or mes == meses:
                evolucao.append({
                    "mes":mes,
                    "montante":montante,
                    "totalAportado":totalAportado,
                    "rendimento":montante - totalAportado
                })

            rendimentoBruto:float = montante - totalAportado
            rendimentoLiquido:float = rendimentoBruto
            ir:float = 0


            if temIR:
                aliquotaIR:float = calcIRRate(meses * 30)
                ir = rendimentoBruto * (aliquotaIR / 100)
                rendimentoLiquido -= ir

            return {
                "simulacao": "Aportes Mensais",
                "valorInicial":valorInicial,
                "aporteMensal":aporteMensal,
                "periodo":meses,
                "taxaAnual":taxaAnual / 100,
                "totalAportado": totalAportado,
                "montanteBruto":montante,
                "rendimentoBruto":rendimentoBruto,
                "impostoRenda": ir if temIR else 0,
                "montanteLiquido":montante - (ir if temIR else 0),
                "rendimentoLiquido":rendimentoLiquido,
                "rentabilidadeTotal":rendimentoLiquido / totalAportado,
                "evolucao":evolucao,
                "formatted":{
                    "valorInicial":formatMoney(valorInicial),
                    "aporteMensal":formatMoney(aporteMensal),
                    "periodo":formatPeriod(meses),
                    "taxaAnual":f"{taxaAnual}%",
                    "totalAportado":formatMoney(totalAportado),
                    "montanteBruto":formatMoney(montante),
                    "rendimentoBruto":formatMoney(rendimentoBruto),
                    "impostoRenda": formatMoney(ir) if temIR else formatMoney(0),
                    "montanteLiquido":formatMoney(montante - (ir if temIR else 0)),
                    "rendimentoLiquido":formatMoney(rendimentoLiquido),
                    "rentabilidadeTotal":formatMoney(rendimentoLiquido / totalAportado)
                }
            }