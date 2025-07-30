from utils import formatMoney

class creditCardCalc:
    def __init__(self):
        ...

    def calcRotativo(self,valorFatura:float,valorPago:float,taxaMensal:float =15):
        if valorPago >= valorFatura:
            return {
                "status":"fatura paga integralmente",
                "valorRotativo":0,
                "custoTotal":0
            }
        
        valorRotativo = valorFatura - valorPago
        juros = valorRotativo * (taxaMensal /100)
        iof = valorRotativo * 0.0038
        custoTotal = juros + iof

        return {
            "valorFatura":valorFatura,
            "valorPago":valorPago,
            "valorRotativo":valorRotativo,
            "juros":juros,
            "iof":iof,
            "custoTotal":custoTotal,
            "proximaFatura":valorRotativo +custoTotal,
            "alerta":"custo alto" if custoTotal > valorRotativo *0.1 else "custo OK",
            "formatted":{
                "valorFatura":formatMoney(valorFatura),
                "valorPago":formatMoney(valorPago),
                "valorRotativo":formatMoney(valorRotativo),
                "juros":formatMoney(juros),
                "iof":formatMoney(iof),
                "custoTotal":formatMoney(custoTotal),
                "proximaFatura":formatMoney(valorRotativo + custoTotal),
                "alerta":"custo alto" if custoTotal > valorRotativo * 0.1 else "custo OK"
                                        }
        }