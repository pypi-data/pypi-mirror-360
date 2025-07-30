import math
def formatMoney(valor:int):
    return f"pt-BR: {valor} BRL"

def parseMoney(valor:float | str) ->float|str:
    try:
        if isinstance(valor,(float,int)):
            return valor
        return float(valor.replace(r"[R$\.\s]"),"").replace(",",".")
    except TypeError as e:
        raise e

def convertRate(taxa:float,de:str,para:str) -> float:
    """valores aceitos no 'de' e no 'para': apenas as palavras
    'mensal' ou 'anual'."""
    if de == "anual" and para == "mensal":
        return (math.pow(1 + taxa / 100,1 / 12) - 1) * 100

    elif de == "mensal" and para == "anual":
        return (math.pow(1 + taxa / 100,12) -1 * 100)
    
    else:
        raise ValueError("valores passados nos parametros 'de' ou 'para' estão incorretos")
    
def calcIRRate(dias:int) ->float:
    if dias <= 180:
        return 22.5
    elif dias <= 360:
        return 20
    elif dias <= 720:
        return 17.5
    else:
        return 15
    

def isValidNumber(valor=None) -> bool:
    return isinstance(valor,(float,int)) and not math.isnan(valor) and math.isfinite(valor)


def validateFinancialParams(valor:float,taxa:float,tempo:float):
    errors:list[str] = []

    if not isValidNumber(valor) or valor <= 0:
        errors.append("valor dever ser um número positivo")

    if not isValidNumber(taxa) or taxa <0:
        errors.append("taxa deve ser um número positivo ou zero")

    if not isValidNumber(tempo) or tempo <= 0:
        errors.append("tempo deve ser um número positivo")

    return {
        "isValid":len(errors) == 0,
        "errors":errors
    }

def formatPeriod(meses:int):
    if meses < 12:
        if meses == 1:
            return f"{meses} mês"
        return f"{meses} meses"

    anos = math.floor(meses / 12)
    mesesRestantes = meses % 12

    resultado = f"{anos} anos" if anos > 1 else f"{anos} ano"

    if mesesRestantes > 0:
        resultado += f"e {mesesRestantes} meses" if mesesRestantes > 1 else f"e {mesesRestantes} mês"

    return resultado


def calcPercentDifference(valor1:float,valor2:float) -> float:
    if valor2 == 0:
        return 0
    return ((valor1 - valor2) / valor2) * 100


def compoundInterest(capital:float,taxaAnual:float,anos:float):
    parcelas = anos * 12
    taxaMensal = convertRate(taxaAnual,"anual","mensal")
    montante = capital * math.pow(1 + taxaMensal / 100,parcelas)

    return {"capital":capital,
            "taxa":taxaMensal,
            "periodo":formatPeriod(anos),
            "montante":round(montante*100)/100,
            "juros":round((montante - capital) * 100)/ 100}