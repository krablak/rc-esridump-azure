# RC-ESRIDUMP-AZURE [REPO BACKUP] 
**rc-esridump-azure** je mini aplikace pro export dat o uzavírkách na silnicích a dálnících ze serverů [ŘSD](https://geoportal.rsd.cz/web) ve formátu [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON). Zdrojová data ŘSD vystavuje ve formě REST API ArcGis serveru na [https://geoportal.rsd.cz/arcgis/rest/](https://geoportal.rsd.cz/arcgis/rest/) a je možné tam najít kromě uzavírek u kupu dalších zajímavostí. A bohužel, kupa dalších dat není veřejně přístupná.

## API
Pro vybrané typy uzavírek máme vystaveny REST metody vracející všechna data ve formátu GeoJSONu a obsahujíc průběh(čára na mapě tvořena body) uzavírek a doplňková metadata popisující uzavírku(Kdy, kde a proč uzavírka je). 

Typicky vypada výstup takto:

        {"type":"FeatureCollection","features":[
            {"geometry": {
                "type": "LineString", 
                "coordinates": [[14.6651886, 49.5383349], [14.6652364, 49.5385102] ...}, 
                "type": "Feature", 
                "properties": {
                    "AlertC3Desc": null, 
                    "Description": "D3, mezi km 62,7  a  62.5, ve sm\u011bru Bene\u0161ov, z\u00fa\u017een\u00e1 vozovka na jeden j\u00edzdn\u00ed pruh, nepr\u016fjezdn\u00fd lev\u00fd j\u00edzdn\u00ed pruh, Od 19.11.2016 17:11 Do 31.12.2018 17:11, Ukon\u010den\u00ed d\u00e1lnice, pokra\u010dov\u00e1n\u00ed na I/3. ", 
                    "OBJECTID": 5444, 
                    "ValidTo": 1546276260000, 
                    "ddrType": "CURRENT", 
                    "IconNumber": "2", 
                    "ROAD_ID": 2665197, 
                    "ChainageTo": 62.9, 
                    "LocalityDesc": "D3, mezi km 62,7  a  62.5, ve sm\u011bru Bene\u0161ov", "AlertC2Desc": "nepr\u016fjezdn\u00fd lev\u00fd j\u00edzdn\u00ed pruh", 
                    "ChainageFrom": 62.92, 
                    "RN": "D3", 
                    "ValidFrom": 1479575460000, 
                    "AlertC1Desc": "z\u00fa\u017een\u00e1 vozovka na jeden j\u00edzdn\u00ed pruh"
                }
            },
            ....

**Upozornění** 

Bohužel u dat silnic druhé a třetí třídy je struktura metadat rozdílná od dálnic a silnic a jednotlivé položky nejsou konzistentní ani mezi sebou. 

### Dálnice - plánované uzavírky 

        curl https://rc-escridump.azurewebsites.net/api/highways-planned?code=wcO1T14hAsWK5bfwYYolZqR13X4V6ZVtp/kHNzkva5iAGeuzP745LQ==

### Dálnice - současné uzavírky 

        curl https://rc-escridump.azurewebsites.net/api/highways-current?code=6Xasb7xlyX6adMlLTAzWt/stVPb/DAcRLAaW0sA7YJcRHlVw8dqnrg==

### Hlavní tahy - plánované uzavírky 

        curl https://rc-escridump.azurewebsites.net/api/roads-planned?code=1c4BeBEcYbw5sBb2/coRJJey9iD1uW5GrOjzbtKPnrGqF3co8dNlTg==

### Hlavní tahy - současné uzavírky 

        curl https://rc-escridump.azurewebsites.net/api/roads-current?code=1nmv/bRrm3DrTYO0QgUL9Zc/a0yHeNog2gBCvKqbEaqggiykKszGBg==

### Silnice 2. a 3. třídy - uzavírky 

        curl https://rc-escridump.azurewebsites.net/api/roads2and3-all?code=msr5mZHL5ehdBagP9tu0WL6Ly69t8NvQP4XYTKqc97i0Hgi0ff1fSw==

## Jak to je udělané
Jak vidíte ve zdrojácích, aplikace je hodně minimalistická a také pěkná úloha na vyzkoušení [serverless](https://en.wikipedia.org/wiki/Serverless_computing) [functions](https://docs.microsoft.com/en-us/azure/azure-functions/). Nepotřebujeme nikde držet stav, jen pomocí [pyesridump](https://github.com/openaddresses/pyesridump) uděláme json a vrátíme jako response. Celé to je nasazené jako funkce/lambda před kterou je http trigger/API Gateway, která směruje requesty na jednotlivé funkce.

Ok. Úplně přesně to na serverless nesedí. Jedna z velkých výhod serveless funkcí má být placení jen za CPU čas, který funkce využije. A v našem případě hromadu času čekáme na odpovědi serveru místo toho abychom počítali.U [lambda funkcí na AWS](https://aws.amazon.com/lambda/) narazíme i na timeout [API Gateway](https://aws.amazon.com/api-gateway/), který je 29 vteřin. A to je na [pyesridump](https://github.com/openaddresses/pyesridump) dump málo.

Naštěstí jsou hledně timeoutu [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/) úplně v pohodě. A na limity jsme zatím nenarazili. [Účtování na Azure Functions](https://azure.microsoft.com/en-us/pricing/details/functions/) je mírně odlišné od AWS, ale tak jako tak je provoz takove funkce, pro naše potřeby, téměř zadarmo.

Azure Functions mají čerstvě podporu pro [python funkce](https://azure.microsoft.com/en-us/updates/azure-functions-python-support-public-preview-2/) a to pro verzi python 3.6 kterou je třeba mít i naistalovanou. Aby to všechno hezky fungovalo je třeba mít nainstalováno:

- Azure Functions Core Tools viz [https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local#v2](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local#v2)

        yarn global add azure-functions-core-tools

- Azure CLI [https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-macos?view=azure-cli-latest](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-macos?view=azure-cli-latest)
- Docker, který je třeba pro build pokud má vaše python funkce nativní závislosti.

Návody a ukázky:

- Jak vytvořit python funkci: [https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-python](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-python)
- Dokumentace k Azure CLI: [https://docs.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest#az_group_create](https://docs.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest#az_group_create)
- Co jsou SKU: [https://docs.microsoft.com/en-us/rest/api/storagerp/srp_sku_types](https://docs.microsoft.com/en-us/rest/api/storagerp/srp_sku_types)
- Jako konfigurovat azure funkci: [https://github.com/Azure/azure-functions-host/wiki/function.json](https://github.com/Azure/azure-functions-host/wiki/function.json)
- Python Functions Guide: [https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- Zavislosti s nutnosti kompilace: [https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python#publishing-to-azure](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python#publishing-to-azure)

Interní cheatsheet:

- Storage: rcstorage000
- Resource group: rc-resource-group
- Vytvoření app:

        az functionapp create --resource-group rc-resource-group --os-type Linux --consumption-plan-location westeurope  --runtime python 
        --name rc-escridump --storage-account  rcstorage000

- Nahrání do azure:

        func azure functionapp publish rc-escridump

- Vytvoření venv:

        python3.6 -m venv .env

- Zapnutí venv: 

        source .env/bin/activate

- Vypnutí venv:

        deactivate

