# client.py

most_tabs = ["Best Opportunities", "Broad Questions", "Narrow Questions"]
all_tabs = most_tabs + ["Near Me"]
important_tabs = most_tabs + ["Important Keywords", "Important URLs"]
qb_tabs = ["Important Keywords", "Best Opportunities", "Narrow Questions", "AI"]

class ClientConfig:
    def __init__(self, project_url, semrush_lookup, semrush_db="us", tabs=None):
        if tabs is None:
            tabs = []
        self.project_url = project_url
        self.semrush_lookup = semrush_lookup
        self.semrush_db = semrush_db
        self.tabs = tabs

class Clients:
    lowes = ClientConfig("https://app.botify.com/lowes/www.lowes.com/", "lowes.com", "us", all_tabs)
    pch = ClientConfig("https://app.botify.com/pch/pch.com/", "pch.com", "us", all_tabs)
    maui_jim = ClientConfig("https://app.botify.com/maui-jim/mauijim.com", "mauijim.com", "us", all_tabs)
    charlotte_observer = ClientConfig("https://app.botify.com/mcclatchy/charlotte/", "charlotteobserver.com", "us", all_tabs)
    star_telegram = ClientConfig("https://app.botify.com/mcclatchy/fort-worth/", "star-telegram.com", "us", all_tabs)
    miami_herald = ClientConfig("https://app.botify.com/mcclatchy/miami/", "miamiherald.com", "us", all_tabs)
    sacbee = ClientConfig("https://app.botify.com/mcclatchy/sacramento/", "sacbee.com", "us", all_tabs)
    kansascity = ClientConfig("https://app.botify.com/mcclatchy/kansas-city/", "kansascity.com", "us", all_tabs)
    quickbooks = ClientConfig("https://app.botify.com/intuit/intuit-quickbooks-600k-monthly-url-js/", "quickbooks.intuit.com", "us", qb_tabs)
    monotaro = ClientConfig("https://app.botify.com/monotaro-team/monotaro.com", "monotaro.com", "jp", all_tabs)
    petsathome = ClientConfig("https://app.botify.com/pets-at-home-org/www.petsathome.com", "petsathome.com", "us", all_tabs)
    bestbuy = ClientConfig("https://app.botify.com/best-buy/best-buy", "bestbuy.com", "us", important_tabs)
    linkedin = ClientConfig("https://app.botify.com/linkedin/crawl-articles/", "www.linkedin.com/pulse/", "us", important_tabs)
    onedoc = ClientConfig("https://app.botify.com/onedoc-org/onedoc.ch", "onedoc.ch", "ch", all_tabs)
    harveynichols = ClientConfig("https://app.botify.com/harvey-nichols-and-company-limited-org/www.harveynichols.com", "harveynichols.com", "uk", all_tabs)
    adidasca = ClientConfig("https://app.botify.com/adidas_org/adidas.ca", "adidas.ca", "ca", all_tabs)
    walmart = ClientConfig("https://app.botify.com/walmart-canada/walmart-canada-10m-monthly-js/", "walmart.com", "us", all_tabs)
    zennioptical = ClientConfig("https://app.botify.com/zenni/www.zennioptical.com/", "zennioptical.com", "us", all_tabs)
    davidsbridal = ClientConfig("https://app.botify.com/davids-bridal-org/davidsbridal.com/", "davidsbridal.com", "us", all_tabs)
    barenecessities = ClientConfig("https://app.botify.com/bare-necessities-org/bare-necessities/", "barenecessities.com", "us", most_tabs)


client = Clients()
