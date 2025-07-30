import requests
from abc import ABC,abstractmethod

class rates(ABC):
    def __init__(self):
        self._selic = 10.75
        self._cdi = 10.5
        self._ipca = 4.5
        self._dolar = 5.2
        self._poupanca = 0.5

    @abstractmethod
    def selic(self):
        pass

    @abstractmethod
    def selic(self):
        pass

    @abstractmethod
    def cdi(self):
        pass

    @abstractmethod
    def cdi(self):
        pass

    @abstractmethod
    def ipca(self):
        pass

    @abstractmethod
    def ipca(self):
        pass

    @abstractmethod
    def dolar(self):
        pass
    
    @abstractmethod
    def dolar(self):
        pass

    @abstractmethod
    def poupanca(self):
        pass
    
    @abstractmethod
    def poupanca(self):
        pass
    


class RatesManager(rates):
    def __init__(self):
        super().__init__()
    
    @property
    def selic(self):
        return self._selic

    @selic.setter
    def selic(self):
        return None

    @property
    def cdi(self):
        return self._cdi

    @cdi.setter
    def cdi(self):
        return None

    @property
    def ipca(self):
        return self._ipca

    @ipca.setter
    def ipca(self):
        return None
   
    @property
    def dolar(self):
        return self._dolar
    
    @dolar.setter
    def dolar(self):
        return None

    @property
    def poupanca(self):
        return self._poupanca
    
    @poupanca.setter
    def poupanca(self):
        return None

    async def updateAll(self) -> rates:
        try:
            selic = await self.fetchSelic()
            if selic:
                self.selic = selic

            self.cdi = self.selic * 0.9

            dolar = await self.fetchDolar()
            if dolar:
                self.dolar = dolar

            self.updateSavingsRule()

            return self
        
        except Exception as e:
            print(f"ocorreu um erro: {e}")
            return None


    def fetchSelic(self) -> float | None:
        try:
            response = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1", params={"formato": "json"})
            dados = response.json()

            if response is not None and isinstance(dados, list) and dados:
                primeiro_item = dados[0]
                valor_str = primeiro_item.get("valor")
                if valor_str is not None:
                    return float(valor_str)
                
            return None
           
        except (requests.exceptions.RequestException,ValueError) as e:
            print(f"ocorreu um erro: {e}")
            return None
        
    def fetchDolar(self)->float | None:
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD",params={"format":"json"})
            dados = response.json()
            if isinstance(dados,dict):
                rates_dict = dados.get("rates")

                if isinstance(rates_dict,dict):
                    valor = rates_dict.get("BRL")
                    return valor
            return None
        except (requests.exceptions.RequestException,ValueError) as e:
            print(f"ocoreu um erro: {e}")
            return None
        
    def updateSavingsRule(self) -> None:
        if self.selic <= 8.5:
            self.poupanca = (self.selic / 12) * 0.7
        else:
            self.poupanca = 0.5

    
    def getAllRates(self) -> dict:
        return {
            "formatted":{
                "selic":f"{self.selic}% a.a",
                "cdi":f"{self.cdi:.2f}% a.a",
                "poupanca":f"{self.poupanca:.2f}% a.m",
                "dolar":f"{self.dolar:.2f}",
                "ipca":f"{self.ipca}% a.a"
            }
            
        }
