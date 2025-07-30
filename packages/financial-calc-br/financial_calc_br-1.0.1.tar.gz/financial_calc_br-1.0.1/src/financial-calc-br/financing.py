from utils import parseMoney,convertRate,formatPeriod,validateFinancialParams,formatMoney
import math

class FinancingCalc:
    def __init__(self):
        ...

    def financingSAC(self,valor:float,taxaAnual:float,anos:float):
        validation = validateFinancialParams(valor,taxaAnual,anos)

        if not validation.get("isValid"):
            erros_str = ",".join(validation.get("errors"))
            raise ValueError(f"Parâmetros inválidos :{erros_str}")
        
        parcelas:float = anos*12
        taxaMensal:float = convertRate(taxaAnual,"anual","mensal")
        amortizacao:float = valor/parcelas

        saldoDevedor:float = valor
        totalJuros:float = 0
        primeiros12:list[dict] = []
        ultimos12:list[dict] = []

        for i in range(1,parcelas + 1):
            juros:float = saldoDevedor * (taxaMensal / 100)
            prestacao:float = amortizacao + juros
            saldoDevedor = max(0,saldoDevedor-amortizacao)
            totalJuros += juros


            if i<= 12:
                primeiros12.append({
                    "parcela":i,
                    "prestacao":prestacao,
                    "juros":juros,
                    "saldo":saldoDevedor
                })
            if i > parcelas - 12:
                ultimos12.append({
                    "parcela":i,
                    "prestacao":prestacao,
                    "juros":juros,
                    "saldo":saldoDevedor
                })

        return{
                "sistema":"SAC",
                "valorFinanciado":valor,
                "prazo":parcelas,
                "taxa":taxaAnual / 100,
                "totalJuros":totalJuros,
                "totalPago":valor + totalJuros,
                "primeiraParcela":amortizacao + (valor * taxaMensal) / 100,
                "ultimaParcela":amortizacao + (amortizacao * taxaMensal) / 100,
                "resumo":{
                    "primeiros12":primeiros12,
                    "ultimos12":ultimos12},
                "formatted":{
                    "sistema":"SAC",
                    "valorFinanciado":formatMoney(valor),
                    "prazo":f"{formatPeriod(parcelas)} ({parcelas}x)",
                    "taxa":f"{taxaAnual}% a.a",
                    "totalJuros":formatMoney(totalJuros),
                    "totalPago":formatMoney(valor + totalJuros),
                    "primeiraParcela":formatMoney(amortizacao + (valor * taxaMensal)/ 100),
                    "ultimaParcela":formatMoney(amortizacao+ (amortizacao + taxaMensal) / 100)
                }

            }
    
    def financingPrince(self,valor:float,taxaAnual:float,anos:float):
        validation = validateFinancialParams(valor,taxaAnual,anos)

        if not validation.get("isValid"):
            erros_str = ",".join(validation.get("errors"))
            raise ValueError(f"Parâmetros inválidos :{erros_str}")
        
        parcelas:float = anos * 12
        taxaMensal:float = convertRate(taxaAnual,"anual","mensal") / 100

        prestacao:float = (valor * (taxaMensal * math.pow(1 + taxaMensal,parcelas))) / (math.pow(1 + taxaMensal,parcelas)- 1)

        saldoDevedor:float = valor
        totalJuros:float = 0
        primeiros12:list[dict] = []
        ultimos12:list[dict] = []

        for i in range(1,parcelas + 1):
            juros:float = saldoDevedor + taxaMensal
            amortizacao:float = prestacao - juros
            saldoDevedor = max(0,saldoDevedor - amortizacao)
            totalJuros += juros


            if i <= 12:
                primeiros12.append({
                    "parcela":i,
                    "prestacao":prestacao,
                    "juros":juros,
                    "amortizacao":amortizacao,
                    "saldo":saldoDevedor
                })

            if i > parcelas - 12:
                ultimos12.append({
                    "parcela":i,
                    "prestacao":prestacao,
                    "juros":juros,
                    "amortizacao":amortizacao,
                    "saldo":saldoDevedor
                })
        return{
            "sistema":"Price",
            "valorFinanciado":valor,
            "prazo":parcelas,
            "taxa":taxaAnual / 100,
            "totalJuros":totalJuros,
            "totalPago":valor + totalJuros,
            "prestacaoFixa":prestacao,
            "resumo":{
                "primeiros12":primeiros12,
                "ultimos12":ultimos12
            },
            "formatted":{
                "sistema":"Price",
                "valorFinanciado":formatMoney(valor),
                "prazo":f"{formatPeriod(parcelas)} ({parcelas}x)",
                "taxa":f"{taxaAnual}% a.a",
                "totalJuros":formatMoney(totalJuros),
                "totalPago":formatMoney(valor + totalJuros),
                "prestacaoFixa":formatMoney(prestacao)
            }
        }
    
    def compareFinancing(self,valor:float,taxaAnual:float,anos:float):
        validation = validateFinancialParams(valor,taxaAnual,anos)

        if not validation.get("isValid"):
            erros_str = ",".join(validation.get("errors"))
            raise ValueError(f"Parâmetros inválidos :{erros_str}")
        
        sac = self.financingSAC(valor,taxaAnual,anos)
        price = self.financingPrince(valor,taxaAnual,anos)

        sacJuros:float = parseMoney(sac.get("totalJuros"))
        priceJuros:float = parseMoney(price.get("totalJuros"))
        economia:float = priceJuros - sacJuros


        return {
            "cenario":{
                "valor":valor,
                "prazo":f"{anos} anos",
                "taxa":f"{taxaAnual}% ao ano"
            },
            "sac":{
                "totalJuros":sac.get("totalJuros"),
                "primeira":sac.get("primeiraParcela"),
                "ultima":sac.get("ultimaParcela"),
                "caracteristicas":[
                    "Parcelas decrescentes",
                    "Menor custo total",
                    "Maior parcela inicial"
                ]
            },
            "price":{
                "totalJuros":price.get("totalJuros"),
                "parcelaFixa":price.get("prestacaoFixa"),
                "caracteristicas":[
                    "Parcelas fixas",
                    "Fácil planejamento",
                    "Maior custo total"
                ]
            },
            "comparacao":{
                "economia":economia,
                "economiaPercentual":economia / priceJuros,
                "recomendacao": self.getRecomendation(
                    sacJuros,priceJuros,parseMoney(sac.get("primeiraParcela")),parseMoney(price.get("prestacaoFixa"))
                ),

                "formatted":{
                    "economia":formatMoney(economia),
                    "economiaPercentual":f"{((economia/priceJuros) * 100):.1f}%"
                }
            }
        }
    


    def getRecomendation(self,sacJuros:float,priceJuros:float,primeiraSAC:float,parcelaPrice:float):
        economiaPercentual:float = ((priceJuros - sacJuros) / priceJuros) * 100

        diferencaParcela:float = ((primeiraSAC - parcelaPrice) / parcelaPrice) * 100

        if economiaPercentual < 5:
            return {
                "sistema":"Price",
                "motivo":"Diferença de custo pequena, parcelas fixas facilitam planejamento"
            }
        elif diferencaParcela > 30:
            return {
                "sistema":"Price",
                "motivo":"Primera parcela SAC muito alta, pode comprometer orçamento"
            }
        else:
            return {
                "sistema":"SAC",
                "motivo":f"Economia significativa de {priceJuros - sacJuros}" 
            }
        
    def simulateDownPayment(self,valorImovel:float,entrada:float,taxaAnual:float,anos:float):
        valorFinanciado:float = valorImovel - entrada
        result = self.compareFinancing(valorFinanciado,taxaAnual,anos)

        return {
            "entrada":entrada,
            "entradaPercentual":entrada / valorImovel,
            "valorFinanciado":valorFinanciado,
            "sac":{
                "primeira":result.get("sac").get("primeira"),
                "ultima":result.get("sac").get("ultima"),
                "totalJuros":result.get("sac").get("totalJuros")
            },
            "price":{
                "parcela":result.get("price").get("parcelaFixa"),
                "totalJuros":result.get("price").get("totalJuros")
            },
            "formatted":{
                "entrada":formatMoney(entrada),
                "entradaPercentual":f"{((entrada / valorImovel) * 100):.0f}%",
                "valorFinanciado":formatMoney(valorFinanciado),
                "sac":{
                    "primeira":formatMoney(result.get("sac").get("primeira")),
                    "ultima":formatMoney(result.get("sac").get("ultima")),
                    "totalJuros":formatMoney(result.get("sac").get("totalJuros"))
                },
                "price":{
                    "parcela":formatMoney(result.get("price").get("parcelaFixa")),
                    "totalJuros":formatMoney(result.get("price").get("totalJuros"))
                }
            },
        }