import re
import csv

def create_redirect_map(bad_urls_raw, good_map_raw):
    """
    This function takes lists of "bad" and "good" URLs and creates a
    dictionary that maps each bad URL to its corresponding good URL.
    """

    # --- Step 1: Parse the 'good' URLs and create a lookup table ---
    # The key will be the store ID, and the value will be the correct URL.
    good_url_lookup = {}
    for item in good_map_raw:
        # We expect the input to be in the format: "URL\tID"
        parts = item.split('\t')
        if len(parts) == 2:
            url = parts[0].strip()
            store_id = parts[1].strip()
            good_url_lookup[store_id] = url

    # --- Step 2: Process the 'bad' URLs and build the redirect map ---
    redirect_map = {}
    for bad_url in bad_urls_raw:
        # Use a regular expression to find the store ID in the bad URL.
        # This pattern looks for one or more digits that follow "/s/".
        match = re.search(r'/s/(\d+)', bad_url)

        if match:
            store_id = match.group(1)
            # If the extracted ID exists in our good URL lookup table...
            if store_id in good_url_lookup:
                # ...then create a mapping from the bad URL to the good one.
                redirect_map[bad_url] = good_url_lookup[store_id]

    return redirect_map

# --- Main execution block ---
if __name__ == "__main__":
    # ❗️ Paste your list of "bad" URLs here
    bad_urls = """
https://discounttire.com/en/store/mi/flint/s/1140
https://www.americastire.com/en/store/CA/Apple%2520Valley/s/1813
https://www.americastire.com/en/store/CA/Camarillo/s/1331
https://www.americastire.com/en/store/CA/Chico/s/1505
https://www.americastire.com/en/store/CA/Fresno/s/1360
https://www.americastire.com/en/store/CA/Gilroy/s/1480
https://www.americastire.com/en/store/CA/Huntington%2520Beach/s/1734
https://www.americastire.com/en/store/CA/La%2520Mesa/s/1067
https://www.americastire.com/en/store/CA/Manteca/s/1917
https://www.americastire.com/en/store/CA/Millbrae/s/1983
https://www.americastire.com/en/store/CA/Orange/s/1948
https://www.americastire.com/en/store/CA/Paso%2520Robles/s/1892
https://www.americastire.com/en/store/CA/Roseville/s/1325
https://www.americastire.com/en/store/CA/San%2520Diego/s/1890
https://www.americastire.com/en/store/CA/Santa%2520Clara/s/1060
https://www.americastire.com/en/store/CA/Thousand%2520Oaks/s/1700
https://www.americastire.com/en/store/CA/Upland/s/1347
https://www.americastire.com/en/store/CA/Vacaville/s/1456
https://www.americastire.com/en/store/CA/Vista/s/1904
https://www.americastire.com/en/store/CA/Walnut%2520Creek/s/1336
https://www.americastire.com/en/store/ca/auburn/s/1868
https://www.americastire.com/en/store/ca/canoga-park/s/1372
https://www.americastire.com/en/store/ca/city-of-industry/s/1526
https://www.americastire.com/en/store/ca/menifee/s/2011
https://www.americastire.com/en/store/ca/palmdale/s/1991
https://www.americastire.com/en/store/ca/simi-valley/s/1330
https://www.americastire.com/en/store/ca/stockton/s/1771
https://www.americastire.com/en/store/ca/torrance/s/1042
https://www.americastire.com/en/store/mi/shelby-charter-township/s/1740
https://www.americastire.com/en/store/or/beaverton/s/1634
https://www.americastire.com/en/store/tx/houston/s/1219
https://www.americastire.com/store/state/city/s/1038
https://www.americastire.com/store/state/city/s/1041
https://www.americastire.com/store/state/city/s/1042
https://www.americastire.com/store/state/city/s/1052
https://www.americastire.com/store/state/city/s/1053
https://www.americastire.com/store/state/city/s/1055
https://www.americastire.com/store/state/city/s/1084
https://www.americastire.com/store/state/city/s/1084/1000
https://www.americastire.com/store/state/city/s/1085
https://www.americastire.com/store/state/city/s/1390
https://www.americastire.com/store/state/city/s/1637
https://www.americastire.com/store/state/city/s/1645
https://www.americastire.com/store/state/city/s/1725
https://www.americastire.com/store/state/city/s/1734
https://www.americastire.com/store/state/city/s/1752
https://www.americastire.com/store/state/city/s/1771
https://www.americastire.com/store/state/city/s/2034
https://www.americastire.com/store/state/city/s/2061
https://www.americastire.com/store/state/city/s/2115
https://www.americastire.com/store/state/city/s/2236
https://www.americastire.com/store/undefined/undefined/s/1063
https://www.americastire.com/store/undefined/undefined/s/1390
https://www.discounttire.com/en/store/AZ/Buckeye/s/1861
https://www.discounttire.com/en/store/AZ/Lake%2520Havasu%2520City/s/1561
https://www.discounttire.com/en/store/AZ/Peoria/s/1025
https://www.discounttire.com/en/store/AZ/Phoenix/s/1018
https://www.discounttire.com/en/store/AZ/Phoenix/s/1472
https://www.discounttire.com/en/store/AZ/Show%2520Low/s/1871
https://www.discounttire.com/en/store/CA/Chula%2520Vista/s/1065
https://www.discounttire.com/en/store/CA/El%2520Cajon/s/1069
https://www.discounttire.com/en/store/CA/Lemon%2520Grove/s/1080
https://www.discounttire.com/en/store/CA/National%2520City/s/1070
https://www.discounttire.com/en/store/CA/Poway/s/1074
https://www.discounttire.com/en/store/CA/San%2520Diego/s/1082
https://www.discounttire.com/en/store/CA/San%2520Diego/s/1549
https://www.discounttire.com/en/store/CA/San%2520Diego/s/1872
https://www.discounttire.com/en/store/CA/San%2520Diego/s/1890
https://www.discounttire.com/en/store/CA/Vista/s/1078
https://www.discounttire.com/en/store/CO/Fort%2520Collins/s/1949
https://www.discounttire.com/en/store/CO/Lakewood/s/1093
https://www.discounttire.com/en/store/FL/Apopka/s/1291
https://www.discounttire.com/en/store/FL/Jacksonville/s/1717
https://www.discounttire.com/en/store/FL/Pensacola/s/1902
https://www.discounttire.com/en/store/FL/Rockledge/s/1894
https://www.discounttire.com/en/store/GA/Conyers/s/1911
https://www.discounttire.com/en/store/GA/Hiram/s/1703
https://www.discounttire.com/en/store/GA/Peachtree%2520City/s/1793
https://www.discounttire.com/en/store/IA/Cedar%2520Rapids/s/1984
https://www.discounttire.com/en/store/IL/Carpentersville/s/1772
https://www.discounttire.com/en/store/IL/Machesney%2520Park/s/1864
https://www.discounttire.com/en/store/IL/Naperville/s/1534
https://www.discounttire.com/en/store/IL/Normal/s/1824
https://www.discounttire.com/en/store/IN/Fort%2520Wayne/s/1701
https://www.discounttire.com/en/store/KS/Olathe/s/1989
https://www.discounttire.com/en/store/KS/Overland%2520Park/s/2042
https://www.discounttire.com/en/store/MI/Ann%2520Arbor/s/1123
https://www.discounttire.com/en/store/MI/Chesterfield/s/1132
https://www.discounttire.com/en/store/MI/Comstock%2520Park/s/1351
https://www.discounttire.com/en/store/MI/Jackson/s/1126
https://www.discounttire.com/en/store/MI/Lathrup%2520Village/s/1644
https://www.discounttire.com/en/store/MI/White%2520Lake/s/2015
https://www.discounttire.com/en/store/MN/Bloomington/s/1571
https://www.discounttire.com/en/store/MN/Burnsville/s/1494
https://www.discounttire.com/en/store/MN/Lino%2520Lakes/s/1576
https://www.discounttire.com/en/store/MN/Maple%2520Grove/s/1893
https://www.discounttire.com/en/store/NC/Denver/s/1801
https://www.discounttire.com/en/store/NC/Hickory/s/1845
https://www.discounttire.com/en/store/NC/High%2520Point/s/1619
https://www.discounttire.com/en/store/NC/Knightdale/s/1643
https://www.discounttire.com/en/store/NM/Roswell/s/1728
https://www.discounttire.com/en/store/NV/Henderson/s/1300
https://www.discounttire.com/en/store/NV/Las%2520Vegas/s/1171
https://www.discounttire.com/en/store/NV/Las%2520Vegas/s/1648
https://www.discounttire.com/en/store/NV/North%2520Las%2520Vegas/s/1440
https://www.discounttire.com/en/store/OH/Grove%2520City/s/1641
https://www.discounttire.com/en/store/OH/Hamilton/s/2031
https://www.discounttire.com/en/store/OK/Moore/s/1817
https://www.discounttire.com/en/store/OR/Clackamas/s/1176
https://www.discounttire.com/en/store/SC/Rock%2520Hill/s/1616
https://www.discounttire.com/en/store/TN/Mount%2520Juliet/s/1755
https://www.discounttire.com/en/store/TX/Baytown/s/1221
https://www.discounttire.com/en/store/TX/Bedford/s/1194
https://www.discounttire.com/en/store/TX/Dallas/s/1190
https://www.discounttire.com/en/store/TX/El%2520Paso/s/1557
https://www.discounttire.com/en/store/TX/Fort%2520Worth/s/1306
https://www.discounttire.com/en/store/TX/Fort%2520Worth/s/1402
https://www.discounttire.com/en/store/TX/Humble/s/1764
https://www.discounttire.com/en/store/TX/Huntsville/s/1364
https://www.discounttire.com/en/store/TX/Katy/s/1296
https://www.discounttire.com/en/store/TX/Katy/s/1750
https://www.discounttire.com/en/store/TX/Leon%2520Valley/s/1254
https://www.discounttire.com/en/store/TX/Lubbock/s/1567
https://www.discounttire.com/en/store/TX/Lubbock/s/1808
https://www.discounttire.com/en/store/TX/Lufkin/s/1416
https://www.discounttire.com/en/store/TX/Missouri%2520City/s/1950
https://www.discounttire.com/en/store/TX/Mount%2520Pleasant/s/1986
https://www.discounttire.com/en/store/TX/Odessa/s/1318
https://www.discounttire.com/en/store/TX/San%2520Antonio/s/1249
https://www.discounttire.com/en/store/TX/San%2520Antonio/s/1314
https://www.discounttire.com/en/store/TX/San%2520Antonio/s/1408
https://www.discounttire.com/en/store/TX/San%2520Antonio/s/1858
https://www.discounttire.com/en/store/TX/Sugar%2520Land/s/1365
https://www.discounttire.com/en/store/TX/Victoria/s/1528
https://www.discounttire.com/en/store/TX/Webster/s/1226
https://www.discounttire.com/en/store/VA/Suffolk/s/2057
https://www.discounttire.com/en/store/WA/Lynnwood/s/1277
https://www.discounttire.com/en/store/WA/Richland/s/1850
https://www.discounttire.com/en/store/WA/Sequim/s/1827
https://www.discounttire.com/en/store/WA/Spokane%2520Valley/s/1263
https://www.discounttire.com/en/store/ar/fayetteville/s/2008
https://www.discounttire.com/en/store/az/mesa/s/1023
https://www.discounttire.com/en/store/az/mesa/s/1294
https://www.discounttire.com/en/store/az/mesa/s/1426
https://www.discounttire.com/en/store/az/phoenix/s/1003
https://www.discounttire.com/en/store/az/phoenix/s/1010
https://www.discounttire.com/en/store/az/phoenix/s/1012
https://www.discounttire.com/en/store/az/phoenix/s/1013
https://www.discounttire.com/en/store/az/phoenix/s/1019
https://www.discounttire.com/en/store/az/phoenix/s/1020
https://www.discounttire.com/en/store/az/prescott/s/1441
https://www.discounttire.com/en/store/az/tucson/s/1033
https://www.discounttire.com/en/store/az/yuma/s/2010
https://www.discounttire.com/en/store/ca/chula-vista/s/1065
https://www.discounttire.com/en/store/ca/san-diego/s/1549
https://www.discounttire.com/en/store/ca/santee/s/1068
https://www.discounttire.com/en/store/co/westminster/s/1308
https://www.discounttire.com/en/store/co/wheat-ridge/s/1097
https://www.discounttire.com/en/store/fl/fleming-island/s/1582
https://www.discounttire.com/en/store/fl/jacksonville/s/1676
https://www.discounttire.com/en/store/ga/alpharetta/s/1585
https://www.discounttire.com/en/store/ga/conyers/s/1911
https://www.discounttire.com/en/store/ga/lilburn/s/1658
https://www.discounttire.com/en/store/ga/smyrna/s/1963
https://www.discounttire.com/en/store/ia/davenport/s/1940
https://www.discounttire.com/en/store/id/hayden/s/1791
https://www.discounttire.com/en/store/id/nampa/s/1924
https://www.discounttire.com/en/store/il/bourbonnais/s/1993
https://www.discounttire.com/en/store/il/glendale-heights/s/1461
https://www.discounttire.com/en/store/il/joliet/s/1536
https://www.discounttire.com/en/store/il/st-charles/s/1971
https://www.discounttire.com/en/store/in/indianapolis/s/1337
https://www.discounttire.com/en/store/ks/derby/s/2005
https://www.discounttire.com/en/store/ks/overland-park/s/2042
https://www.discounttire.com/en/store/ky/louisville/s/2024
https://www.discounttire.com/en/store/mi/battle-creek/s/1591
https://www.discounttire.com/en/store/mi/commerce-township/s/1404
https://www.discounttire.com/en/store/mi/new-hudson/s/1627
https://www.discounttire.com/en/store/mi/white-lake/s/2015
https://www.discounttire.com/en/store/mn/waite-park/s/1832
https://www.discounttire.com/en/store/mo/joplin/s/2013
https://www.discounttire.com/en/store/mt/kalispell/s/2027
https://www.discounttire.com/en/store/nc/cary/s/1647
https://www.discounttire.com/en/store/nc/charlotte/s/1969
https://www.discounttire.com/en/store/nc/raleigh/s/1914
https://www.discounttire.com/en/store/nc/wake-forest/s/1642
https://www.discounttire.com/en/store/ne/omaha/s/1932
https://www.discounttire.com/en/store/nm/alamogordo/s/1908
https://www.discounttire.com/en/store/oh/columbus/s/1338
https://www.discounttire.com/en/store/oh/miamisburg/s/1500
https://www.discounttire.com/en/store/oh/parma-heights/s/1978
https://www.discounttire.com/en/store/ok/tulsa/s/1929
https://www.discounttire.com/en/store/or/beaverton/s/1634
https://www.discounttire.com/en/store/or/bend/s/1693
https://www.discounttire.com/en/store/sc/fort-mill/s/1937
https://www.discounttire.com/en/store/sc/indian-land/s/1882
https://www.discounttire.com/en/store/tn/Gallatin/s/1804
https://www.discounttire.com/en/store/tn/clarksville/s/1982
https://www.discounttire.com/en/store/tn/cordova/s/2022
https://www.discounttire.com/en/store/tx/austin/s/1279
https://www.discounttire.com/en/store/tx/boerne/s/2012
https://www.discounttire.com/en/store/tx/burleson/s/1532
https://www.discounttire.com/en/store/tx/college-station/s/2000
https://www.discounttire.com/en/store/tx/el-paso/s/1705
https://www.discounttire.com/en/store/tx/harker-heights/s/1852
https://www.discounttire.com/en/store/tx/houston/s/1213
https://www.discounttire.com/en/store/tx/houston/s/1334
https://www.discounttire.com/en/store/tx/laredo/s/1942
https://www.discounttire.com/en/store/tx/leander/s/1972
https://www.discounttire.com/en/store/tx/mckinney/s/1382
https://www.discounttire.com/en/store/tx/missouri-city/s/1950
https://www.discounttire.com/en/store/tx/mount-pleasant/s/1986
https://www.discounttire.com/en/store/tx/new-braunfels/s/1889
https://www.discounttire.com/en/store/tx/plano/s/1186
https://www.discounttire.com/en/store/tx/rockwall/s/1386
https://www.discounttire.com/en/store/tx/san-antonio/s/1249
https://www.discounttire.com/en/store/ut/washington/s/1570
https://www.discounttire.com/en/store/wa/burien/s/1273
https://www.discounttire.com/en/store/wa/seattle/s/1273
https://www.discounttire.com/store/state/city/s/1002
https://www.discounttire.com/store/state/city/s/1005
https://www.discounttire.com/store/state/city/s/1009
https://www.discounttire.com/store/state/city/s/1011
https://www.discounttire.com/store/state/city/s/1023
https://www.discounttire.com/store/state/city/s/1027
https://www.discounttire.com/store/state/city/s/1038
https://www.discounttire.com/store/state/city/s/1041
https://www.discounttire.com/store/state/city/s/1055
https://www.discounttire.com/store/state/city/s/1065
https://www.discounttire.com/store/state/city/s/1080
https://www.discounttire.com/store/state/city/s/1091
https://www.discounttire.com/store/state/city/s/1102
https://www.discounttire.com/store/state/city/s/1111
https://www.discounttire.com/store/state/city/s/1113
https://www.discounttire.com/store/state/city/s/1122
https://www.discounttire.com/store/state/city/s/1127
https://www.discounttire.com/store/state/city/s/1131
https://www.discounttire.com/store/state/city/s/1133
https://www.discounttire.com/store/state/city/s/1136
https://www.discounttire.com/store/state/city/s/1140
https://www.discounttire.com/store/state/city/s/1151
https://www.discounttire.com/store/state/city/s/1153
https://www.discounttire.com/store/state/city/s/1156
https://www.discounttire.com/store/state/city/s/1157
https://www.discounttire.com/store/state/city/s/1164
https://www.discounttire.com/store/state/city/s/1173
https://www.discounttire.com/store/state/city/s/1175
https://www.discounttire.com/store/state/city/s/1177
https://www.discounttire.com/store/state/city/s/1190
https://www.discounttire.com/store/state/city/s/1194
https://www.discounttire.com/store/state/city/s/1203
https://www.discounttire.com/store/state/city/s/1236
https://www.discounttire.com/store/state/city/s/1238
https://www.discounttire.com/store/state/city/s/1246
https://www.discounttire.com/store/state/city/s/1252
https://www.discounttire.com/store/state/city/s/1260
https://www.discounttire.com/store/state/city/s/1263
https://www.discounttire.com/store/state/city/s/1265
https://www.discounttire.com/store/state/city/s/1268
https://www.discounttire.com/store/state/city/s/1268/solicitedReview
https://www.discounttire.com/store/state/city/s/1269
https://www.discounttire.com/store/state/city/s/1277
https://www.discounttire.com/store/state/city/s/1283
https://www.discounttire.com/store/state/city/s/1284
https://www.discounttire.com/store/state/city/s/1285
https://www.discounttire.com/store/state/city/s/1290
https://www.discounttire.com/store/state/city/s/1305
https://www.discounttire.com/store/state/city/s/1322
https://www.discounttire.com/store/state/city/s/1334
https://www.discounttire.com/store/state/city/s/1339
https://www.discounttire.com/store/state/city/s/1354
https://www.discounttire.com/store/state/city/s/1366
https://www.discounttire.com/store/state/city/s/1389
https://www.discounttire.com/store/state/city/s/1396
https://www.discounttire.com/store/state/city/s/1406
https://www.discounttire.com/store/state/city/s/1419
https://www.discounttire.com/store/state/city/s/1421
https://www.discounttire.com/store/state/city/s/1428
https://www.discounttire.com/store/state/city/s/1433
https://www.discounttire.com/store/state/city/s/1441
https://www.discounttire.com/store/state/city/s/1448
https://www.discounttire.com/store/state/city/s/1451
https://www.discounttire.com/store/state/city/s/1474
https://www.discounttire.com/store/state/city/s/1492
https://www.discounttire.com/store/state/city/s/1504
https://www.discounttire.com/store/state/city/s/1522
https://www.discounttire.com/store/state/city/s/1527
https://www.discounttire.com/store/state/city/s/1534
https://www.discounttire.com/store/state/city/s/1537
https://www.discounttire.com/store/state/city/s/1538
https://www.discounttire.com/store/state/city/s/1553
https://www.discounttire.com/store/state/city/s/1561
https://www.discounttire.com/store/state/city/s/1568
https://www.discounttire.com/store/state/city/s/1610
https://www.discounttire.com/store/state/city/s/1620
https://www.discounttire.com/store/state/city/s/1628
https://www.discounttire.com/store/state/city/s/1637
https://www.discounttire.com/store/state/city/s/1645
https://www.discounttire.com/store/state/city/s/1659
https://www.discounttire.com/store/state/city/s/1666
https://www.discounttire.com/store/state/city/s/1681
https://www.discounttire.com/store/state/city/s/1682
https://www.discounttire.com/store/state/city/s/1683
https://www.discounttire.com/store/state/city/s/1690
https://www.discounttire.com/store/state/city/s/1692
https://www.discounttire.com/store/state/city/s/1706
https://www.discounttire.com/store/state/city/s/1717
https://www.discounttire.com/store/state/city/s/1721
https://www.discounttire.com/store/state/city/s/1725
https://www.discounttire.com/store/state/city/s/1726
https://www.discounttire.com/store/state/city/s/1730
https://www.discounttire.com/store/state/city/s/1739
https://www.discounttire.com/store/state/city/s/1745
https://www.discounttire.com/store/state/city/s/1746
https://www.discounttire.com/store/state/city/s/1747
https://www.discounttire.com/store/state/city/s/1751
https://www.discounttire.com/store/state/city/s/1755
https://www.discounttire.com/store/state/city/s/1756
https://www.discounttire.com/store/state/city/s/1763
https://www.discounttire.com/store/state/city/s/1764
https://www.discounttire.com/store/state/city/s/1770
https://www.discounttire.com/store/state/city/s/1773
https://www.discounttire.com/store/state/city/s/1774
https://www.discounttire.com/store/state/city/s/1786
https://www.discounttire.com/store/state/city/s/1818
https://www.discounttire.com/store/state/city/s/1822
https://www.discounttire.com/store/state/city/s/1831
https://www.discounttire.com/store/state/city/s/1833
https://www.discounttire.com/store/state/city/s/1838
https://www.discounttire.com/store/state/city/s/1839
https://www.discounttire.com/store/state/city/s/1844
https://www.discounttire.com/store/state/city/s/1847
https://www.discounttire.com/store/state/city/s/1849
https://www.discounttire.com/store/state/city/s/1852
https://www.discounttire.com/store/state/city/s/1861
https://www.discounttire.com/store/state/city/s/1863
https://www.discounttire.com/store/state/city/s/1864
https://www.discounttire.com/store/state/city/s/1866
https://www.discounttire.com/store/state/city/s/1872
https://www.discounttire.com/store/state/city/s/1878
https://www.discounttire.com/store/state/city/s/1889
https://www.discounttire.com/store/state/city/s/1910
https://www.discounttire.com/store/state/city/s/1925
https://www.discounttire.com/store/state/city/s/1928
https://www.discounttire.com/store/state/city/s/1947
https://www.discounttire.com/store/state/city/s/1947/solicitedReview
https://www.discounttire.com/store/state/city/s/1957
https://www.discounttire.com/store/state/city/s/1982
https://www.discounttire.com/store/state/city/s/1985
https://www.discounttire.com/store/state/city/s/2022
https://www.discounttire.com/store/state/city/s/2025
https://www.discounttire.com/store/state/city/s/2029
https://www.discounttire.com/store/state/city/s/2031
https://www.discounttire.com/store/state/city/s/2034
https://www.discounttire.com/store/state/city/s/2040
https://www.discounttire.com/store/state/city/s/2049
https://www.discounttire.com/store/state/city/s/2054
https://www.discounttire.com/store/state/city/s/2058
https://www.discounttire.com/store/state/city/s/2059
https://www.discounttire.com/store/state/city/s/2061
https://www.discounttire.com/store/state/city/s/2062
https://www.discounttire.com/store/state/city/s/2065
https://www.discounttire.com/store/state/city/s/2071
https://www.discounttire.com/store/state/city/s/2074
https://www.discounttire.com/store/state/city/s/2075
https://www.discounttire.com/store/state/city/s/2080
https://www.discounttire.com/store/state/city/s/2086
https://www.discounttire.com/store/state/city/s/2088
https://www.discounttire.com/store/state/city/s/2090
https://www.discounttire.com/store/state/city/s/2095
https://www.discounttire.com/store/state/city/s/2103
https://www.discounttire.com/store/state/city/s/2118
https://www.discounttire.com/store/state/city/s/2119
https://www.discounttire.com/store/state/city/s/2127
https://www.discounttire.com/store/state/city/s/2153
https://www.discounttire.com/store/state/city/s/2166
https://www.discounttire.com/store/state/city/s/2224
https://www.discounttire.com/store/state/city/s/2227
https://www.discounttire.com/store/state/city/s/2233
https://www.discounttire.com/store/state/city/s/2235
https://www.discounttire.com/store/state/city/s/2238
https://www.discounttire.com/store/state/city/s/2239
https://www.discounttire.com/store/state/city/s/2240
https://www.discounttire.com/store/state/city/s/2241
https://www.discounttire.com/store/state/city/s/2242
https://www.discounttire.com/store/state/city/s/2245
https://www.discounttire.com/store/state/city/s/2247
https://www.discounttire.com/store/state/city/s/2251
https://www.discounttire.com/store/state/city/s/2252
https://www.discounttire.com/store/state/city/s/2255
https://www.discounttire.com/store/state/city/s/2261
https://www.discounttire.com/store/state/city/s/2262
https://www.discounttire.com/store/state/city/s/2264
https://www.discounttire.com/store/state/city/s/2267
https://www.discounttire.com/store/state/city/s/2268
https://www.discounttire.com/store/state/city/s/2269
https://www.discounttire.com/store/state/city/s/2270
https://www.discounttire.com/store/state/city/s/2271
https://www.discounttire.com/store/state/city/s/2272
https://www.discounttire.com/store/undefined/undefined/s/1344
https://www.discounttire.com/store/undefined/undefined/s/1817/

    """.strip().split("\n")

    # ❗️ Paste your list of "good" URLs and their IDs here
    good_map_input = """
https://www.americastire.com/store/ca/bakersfield/s/1785	1785
https://www.americastire.com/store/ca/cathedral-city/s/1084	1084
https://www.americastire.com/store/ca/chino-hills/s/1597	1597
https://www.americastire.com/store/ca/dublin/s/1482	1482
https://www.americastire.com/store/ca/fontana/s/1870	1870
https://www.americastire.com/store/ca/gilroy/s/1480	1480
https://www.americastire.com/store/ca/huntington-beach/s/1390	1390
https://www.americastire.com/store/ca/modesto/s/1058	1058
https://www.americastire.com/store/ca/moreno-valley/s/1518	1518
https://www.americastire.com/store/ca/mountain-view/s/1063	1063
https://www.americastire.com/store/ca/norwalk/s/2046	2046
https://www.americastire.com/store/ca/redwood-city/s/1059	1059
https://www.americastire.com/store/ca/riverside/s/1348	1348
https://www.americastire.com/store/ca/salinas/s/1481	1481
https://www.americastire.com/store/ca/santa-maria/s/1709	1709
https://www.americastire.com/store/ca/thousand-oaks/s/1700	1700
https://www.americastire.com/store/ca/torrance/s/1042	1042
https://www.americastire.com/store/ca/ventura/s/1476	1476
https://www.americastire.com/store/ca/west-sacramento/s/1829	1829
https://www.americastire.com/store/ca/clovis/s/2313	2313
https://www.americastire.com/store/pa/scranton/s/2321	2321
https://www.americastire.com/store/ca/antelope/s/2180	2180
https://www.americastire.com/store/ca/bakersfield/s/1546	1546
https://www.americastire.com/store/ca/brentwood/s/1725	1725
https://www.americastire.com/store/ca/campbell/s/1061	1061
https://www.americastire.com/store/ca/chico/s/1505	1505
https://www.americastire.com/store/ca/chino/s/1038	1038
https://www.americastire.com/store/ca/coachella/s/2081	2081
https://www.americastire.com/store/ca/el-centro/s/1572	1572
https://www.americastire.com/store/ca/elk-grove/s/1637	1637
https://www.americastire.com/store/ca/fremont/s/1052	1052
https://www.americastire.com/store/ca/fullerton/s/1087	1087
https://www.americastire.com/store/ca/garden-grove/s/1286	1286
https://www.americastire.com/store/ca/glendale/s/1752	1752
https://www.americastire.com/store/ca/hesperia/s/1548	1548
https://www.americastire.com/store/ca/jackson/s/1952	1952
https://www.americastire.com/store/ca/lake-forest/s/1086	1086
https://www.americastire.com/store/ca/menifee/s/2011	2011
https://www.americastire.com/store/ca/merced/s/2034	2034
https://www.americastire.com/store/ca/moreno-valley/s/2178	2178
https://www.americastire.com/store/ca/northridge/s/1046	1046
https://www.americastire.com/store/ca/orangevale/s/1050	1050
https://www.americastire.com/store/ca/paso-robles/s/1892	1892
https://www.americastire.com/store/ca/rocklin/s/1875	1875
https://www.americastire.com/store/ca/roseville/s/1325	1325
https://www.americastire.com/store/ca/simi-valley/s/1330	1330
https://www.americastire.com/store/ca/stockton/s/1310	1310
https://www.americastire.com/store/ca/stockton/s/1771	1771
https://www.americastire.com/store/ca/temecula/s/1385	1385
https://www.americastire.com/store/ca/turlock/s/1645	1645
https://www.americastire.com/store/ca/union-city/s/1062	1062
https://www.americastire.com/store/ca/vacaville/s/1456	1456
https://www.americastire.com/store/ca/yuba-city/s/2236	2236
https://www.americastire.com/store/ca/san-jose/s/2228	2228
https://www.americastire.com/store/ca/lodi/s/2289	2289
https://www.americastire.com/store/pa/wilkes-barre/s/2336	2336
https://www.americastire.com/store/pa/whitehall/s/2378	2378
https://www.americastire.com/store/ca/carson/s/1044	1044
https://www.americastire.com/store/ca/city-of-industry/s/1526	1526
https://www.americastire.com/store/ca/concord/s/1053	1053
https://www.americastire.com/store/ca/fresno/s/1360	1360
https://www.americastire.com/store/ca/glendora/s/1370	1370
https://www.americastire.com/store/ca/hemet/s/1392	1392
https://www.americastire.com/store/ca/indio/s/1085	1085
https://www.americastire.com/store/ca/livermore/s/1350	1350
https://www.americastire.com/store/ca/manteca/s/1917	1917
https://www.americastire.com/store/ca/murrieta/s/1506	1506
https://www.americastire.com/store/ca/norco/s/1045	1045
https://www.americastire.com/store/ca/orange/s/1948	1948
https://www.americastire.com/store/ca/palm-desert/s/1639	1639
https://www.americastire.com/store/ca/palm-springs/s/1879	1879
https://www.americastire.com/store/ca/palo-alto/s/2047	2047
https://www.americastire.com/store/ca/rohnert-park/s/2023	2023
https://www.americastire.com/store/ca/sacramento/s/1055	1055
https://www.americastire.com/store/ca/sacramento/s/2115	2115
https://www.americastire.com/store/ca/san-ramon/s/1828	1828
https://www.americastire.com/store/ca/santa-clara/s/1060	1060
https://www.americastire.com/store/ca/signal-hill/s/1821	1821
https://www.americastire.com/store/ca/tracy/s/1524	1524
https://www.americastire.com/store/ca/victorville/s/1039	1039
https://www.americastire.com/store/ca/walnut-creek/s/1336	1336
https://www.americastire.com/store/ca/west-covina/s/2061	2061
https://www.americastire.com/store/ca/folsom/s/1450	1450
https://www.americastire.com/store/ca/redding/s/1064	1064
https://www.americastire.com/store/ca/san-clemente/s/2308	2308
https://www.americastire.com/store/ca/stockton/s/2256	2256
https://www.americastire.com/store/ca/cerritos/s/2273	2273
https://www.americastire.com/store/pa/exton/s/2411	2411
https://www.americastire.com/store/ca/apple-valley/s/1813	1813
https://www.americastire.com/store/ca/camarillo/s/1331	1331
https://www.americastire.com/store/ca/canoga-park/s/1372	1372
https://www.americastire.com/store/ca/clovis/s/1359	1359
https://www.americastire.com/store/ca/colton/s/1760	1760
https://www.americastire.com/store/ca/corona/s/1876	1876
https://www.americastire.com/store/ca/costa-mesa/s/1458	1458
https://www.americastire.com/store/ca/fresno/s/2217	2217
https://www.americastire.com/store/ca/goleta/s/2107	2107
https://www.americastire.com/store/ca/huntington-beach/s/1734	1734
https://www.americastire.com/store/ca/lancaster/s/1043	1043
https://www.americastire.com/store/ca/millbrae/s/1983	1983
https://www.americastire.com/store/ca/mission-viejo/s/1357	1357
https://www.americastire.com/store/ca/modesto/s/2167	2167
https://www.americastire.com/store/ca/montclair/s/1040	1040
https://www.americastire.com/store/ca/napa/s/1363	1363
https://www.americastire.com/store/ca/ontario/s/1383	1383
https://www.americastire.com/store/ca/palmdale/s/1991	1991
https://www.americastire.com/store/ca/pasadena/s/1047	1047
https://www.americastire.com/store/ca/pittsburg/s/2237	2237
https://www.americastire.com/store/ca/rancho-cordova/s/1343	1343
https://www.americastire.com/store/ca/rancho-palos-verdes/s/1048	1048
https://www.americastire.com/store/ca/riverbank/s/2035	2035
https://www.americastire.com/store/ca/riverside/s/1041	1041
https://www.americastire.com/store/ca/san-jose/s/1051	1051
https://www.americastire.com/store/ca/san-luis-obispo/s/1901	1901
https://www.americastire.com/store/ca/santa-clarita/s/1539	1539
https://www.americastire.com/store/ca/santa-rosa/s/1342	1342
https://www.americastire.com/store/ca/temecula/s/1663	1663
https://www.americastire.com/store/ca/torrance/s/1345	1345
https://www.americastire.com/store/ca/upland/s/1347	1347
https://www.americastire.com/store/ca/visalia/s/1976	1976
https://www.americastire.com/store/ca/auburn/s/1868	1868
https://www.americastire.com/store/ca/fontana/s/2248	2248
https://www.americastire.com/store/ca/placerville/s/2379	2379
https://www.discounttire.com/store/al/birmingham/s/2199	2199
https://www.discounttire.com/store/al/montgomery/s/2218	2218
https://www.discounttire.com/store/ar/jonesboro/s/2189	2189
https://www.discounttire.com/store/ar/north-little-rock/s/2166	2166
https://www.discounttire.com/store/ca/chula-vista/s/1065	1065
https://www.discounttire.com/store/ca/escondido/s/1355	1355
https://www.discounttire.com/store/ca/la-mesa/s/1067	1067
https://www.discounttire.com/store/ca/san-diego/s/1890	1890
https://www.discounttire.com/store/ca/santee/s/1068	1068
https://www.discounttire.com/store/ca/solana-beach/s/1072	1072
https://www.discounttire.com/store/fl/panama-city/s/2158	2158
https://www.discounttire.com/store/ga/athens/s/2096	2096
https://www.discounttire.com/store/ga/douglasville/s/1485	1485
https://www.discounttire.com/store/ga/duluth/s/1718	1718
https://www.discounttire.com/store/ga/evans/s/2147	2147
https://www.discounttire.com/store/ga/hinesville/s/2210	2210
https://www.discounttire.com/store/ga/peachtree-city/s/1793	1793
https://www.discounttire.com/store/ga/stockbridge/s/1720	1720
https://www.discounttire.com/store/ga/woodstock/s/1737	1737
https://www.discounttire.com/store/ky/bowling-green/s/1930	1930
https://www.discounttire.com/store/ky/louisville/s/2054	2054
https://www.discounttire.com/store/la/shreveport/s/2144	2144
https://www.discounttire.com/store/mo/joplin/s/2013	2013
https://www.discounttire.com/store/nc/asheville/s/1895	1895
https://www.discounttire.com/store/nc/burlington/s/1783	1783
https://www.discounttire.com/store/nc/charlotte/s/1510	1510
https://www.discounttire.com/store/nc/concord/s/1453	1453
https://www.discounttire.com/store/nc/denver/s/1801	1801
https://www.discounttire.com/store/nc/gastonia/s/1428	1428
https://www.discounttire.com/store/nc/high-point/s/1619	1619
https://www.discounttire.com/store/nc/jacksonville/s/2156	2156
https://www.discounttire.com/store/nc/wake-forest/s/1642	1642
https://www.discounttire.com/store/nc/wilmington/s/2220	2220
https://www.discounttire.com/store/nc/wilson/s/2133	2133
https://www.discounttire.com/store/nc/winston-salem/s/1593	1593
https://www.discounttire.com/store/ne/omaha/s/1962	1962
https://www.discounttire.com/store/nv/henderson/s/1312	1312
https://www.discounttire.com/store/nv/henderson/s/1847	1847
https://www.discounttire.com/store/nv/henderson/s/2205	2205
https://www.discounttire.com/store/nv/las-vegas/s/1169	1169
https://www.discounttire.com/store/nv/las-vegas/s/1172	1172
https://www.discounttire.com/store/nv/las-vegas/s/2050	2050
https://www.discounttire.com/store/nv/north-las-vegas/s/1440	1440
https://www.discounttire.com/store/ok/bartlesville/s/2193	2193
https://www.discounttire.com/store/ok/broken-arrow/s/1912	1912
https://www.discounttire.com/store/ok/edmond/s/1844	1844
https://www.discounttire.com/store/ok/enid/s/2151	2151
https://www.discounttire.com/store/ok/moore/s/1817	1817
https://www.discounttire.com/store/ok/oklahoma-city/s/2089	2089
https://www.discounttire.com/store/sc/florence/s/2032	2032
https://www.discounttire.com/store/sc/north-myrtle-beach/s/2214	2214
https://www.discounttire.com/store/sc/summerville/s/2211	2211
https://www.discounttire.com/store/sc/taylors/s/1775	1775
https://www.discounttire.com/store/tn/cordova/s/2022	2022
https://www.discounttire.com/store/tn/spring-hill/s/1830	1830
https://www.discounttire.com/store/al/montgomery/s/2284	2284
https://www.discounttire.com/store/az/chandler/s/2194	2194
https://www.discounttire.com/store/az/cottonwood/s/1938	1938
https://www.discounttire.com/store/az/fountain-hills/s/1633	1633
https://www.discounttire.com/store/az/glendale/s/1283	1283
https://www.discounttire.com/store/az/glendale/s/1512	1512
https://www.discounttire.com/store/az/peoria/s/2080	2080
https://www.discounttire.com/store/az/phoenix/s/1012	1012
https://www.discounttire.com/store/az/phoenix/s/1013	1013
https://www.discounttire.com/store/az/phoenix/s/1358	1358
https://www.discounttire.com/store/az/phoenix/s/1472	1472
https://www.discounttire.com/store/az/queen-creek/s/1795	1795
https://www.discounttire.com/store/az/scottsdale/s/1284	1284
https://www.discounttire.com/store/az/scottsdale/s/1344	1344
https://www.discounttire.com/store/az/tempe/s/1352	1352
https://www.discounttire.com/store/az/tucson/s/1030	1030
https://www.discounttire.com/store/az/tucson/s/1967	1967
https://www.discounttire.com/store/fl/sanford/s/1317	1317
https://www.discounttire.com/store/ga/johns-creek/s/2254	2254
https://www.discounttire.com/store/nm/albuquerque/s/1773	1773
https://www.discounttire.com/store/tn/nashville/s/2007	2007
https://www.discounttire.com/store/tx/amarillo/s/1409	1409
https://www.discounttire.com/store/tx/arlington/s/1200	1200
https://www.discounttire.com/store/tx/austin/s/1712	1712
https://www.discounttire.com/store/tx/beaumont/s/1236	1236
https://www.discounttire.com/store/tx/brenham/s/1696	1696
https://www.discounttire.com/store/tx/brownsville/s/1607	1607
https://www.discounttire.com/store/tx/burleson/s/1532	1532
https://www.discounttire.com/store/tx/carrollton/s/1189	1189
https://www.discounttire.com/store/tx/carrollton/s/1293	1293
https://www.discounttire.com/store/tx/cleburne/s/1878	1878
https://www.discounttire.com/store/tx/clute/s/2106	2106
https://www.discounttire.com/store/tx/crossroads/s/1799	1799
https://www.discounttire.com/store/tx/denton/s/2140	2140
https://www.discounttire.com/store/tx/el-paso/s/1209	1209
https://www.discounttire.com/store/tx/fort-worth/s/1193	1193
https://www.discounttire.com/store/tx/fort-worth/s/1306	1306
https://www.discounttire.com/store/tx/fort-worth/s/1393	1393
https://www.discounttire.com/store/tx/fort-worth/s/2172	2172
https://www.discounttire.com/store/tx/haslet/s/2075	2075
https://www.discounttire.com/store/tx/houston/s/1212	1212
https://www.discounttire.com/store/tx/houston/s/1243	1243
https://www.discounttire.com/store/tx/houston/s/1288	1288
https://www.discounttire.com/store/tx/houston/s/2085	2085
https://www.discounttire.com/store/tx/huntsville/s/1364	1364
https://www.discounttire.com/store/tx/irving/s/1201	1201
https://www.discounttire.com/store/tx/katy/s/1479	1479
https://www.discounttire.com/store/tx/kerrville/s/1630	1630
https://www.discounttire.com/store/tx/kyle/s/1853	1853
https://www.discounttire.com/store/tx/la-porte/s/1601	1601
https://www.discounttire.com/store/tx/lake-worth/s/1434	1434
https://www.discounttire.com/store/tx/league-city/s/1419	1419
https://www.discounttire.com/store/tx/livingston/s/2120	2120
https://www.discounttire.com/store/tx/lubbock/s/1808	1808
https://www.discounttire.com/store/tx/lufkin/s/1416	1416
https://www.discounttire.com/store/tx/mansfield/s/1656	1656
https://www.discounttire.com/store/tx/mcallen/s/1407	1407
https://www.discounttire.com/store/tx/midland/s/1731	1731
https://www.discounttire.com/store/tx/plano/s/1203	1203
https://www.discounttire.com/store/tx/plano/s/1340	1340
https://www.discounttire.com/store/tx/plano/s/1341	1341
https://www.discounttire.com/store/tx/plano/s/2139	2139
https://www.discounttire.com/store/tx/portland/s/2006	2006
https://www.discounttire.com/store/tx/rosenberg/s/1424	1424
https://www.discounttire.com/store/tx/san-angelo/s/1439	1439
https://www.discounttire.com/store/tx/san-antonio/s/1314	1314
https://www.discounttire.com/store/tx/selma/s/1600	1600
https://www.discounttire.com/store/tx/sugar-land/s/1365	1365
https://www.discounttire.com/store/tx/texas-city/s/1437	1437
https://www.discounttire.com/store/tx/tyler/s/1944	1944
https://www.discounttire.com/store/tx/tyler/s/2165	2165
https://www.discounttire.com/store/tx/waxahachie/s/1762	1762
https://www.discounttire.com/store/va/mechanicsville/s/2272	2272
https://www.discounttire.com/store/az/anthem/s/1651	1651
https://www.discounttire.com/store/az/mesa/s/1023	1023
https://www.discounttire.com/store/az/mesa/s/1294	1294
https://www.discounttire.com/store/az/peoria/s/1857	1857
https://www.discounttire.com/store/az/tucson/s/1411	1411
https://www.discounttire.com/store/fl/milton/s/2239	2239
https://www.discounttire.com/store/ia/cedar-falls/s/1998	1998
https://www.discounttire.com/store/ia/davenport/s/1940	1940
https://www.discounttire.com/store/ia/davenport/s/1960	1960
https://www.discounttire.com/store/id/meridian/s/1921	1921
https://www.discounttire.com/store/il/springfield/s/1537	1537
https://www.discounttire.com/store/ks/lawrence/s/1958	1958
https://www.discounttire.com/store/ks/manhattan/s/2260	2260
https://www.discounttire.com/store/ks/overland-park/s/2055	2055
https://www.discounttire.com/store/mo/belton/s/1934	1934
https://www.discounttire.com/store/mo/blue-springs/s/2033	2033
https://www.discounttire.com/store/mo/independence/s/2020	2020
https://www.discounttire.com/store/mo/kansas-city/s/2177	2177
https://www.discounttire.com/store/mo/saint-joseph/s/2049	2049
https://www.discounttire.com/store/mt/billings/s/2159	2159
https://www.discounttire.com/store/ne/grand-island/s/2130	2130
https://www.discounttire.com/store/ne/papillion/s/1999	1999
https://www.discounttire.com/store/oh/mentor/s/2212	2212
https://www.discounttire.com/store/or/clackamas/s/1176	1176
https://www.discounttire.com/store/or/hillsboro/s/1903	1903
https://www.discounttire.com/store/or/oregon-city/s/2025	2025
https://www.discounttire.com/store/sc/greenville/s/1608	1608
https://www.discounttire.com/store/sd/sioux-falls/s/2146	2146
https://www.discounttire.com/store/tx/cypress/s/1920	1920
https://www.discounttire.com/store/tx/houston/s/1470	1470
https://www.discounttire.com/store/tx/houston/s/1560	1560
https://www.discounttire.com/store/tx/humble/s/1235	1235
https://www.discounttire.com/store/tx/humble/s/1389	1389
https://www.discounttire.com/store/tx/katy/s/2213	2213
https://www.discounttire.com/store/tx/little-elm/s/1757	1757
https://www.discounttire.com/store/tx/pearland/s/1436	1436
https://www.discounttire.com/store/tx/shenandoah/s/1511	1511
https://www.discounttire.com/store/tx/the-colony/s/1533	1533
https://www.discounttire.com/store/tx/the-woodlands/s/1239	1239
https://www.discounttire.com/store/ut/clearfield/s/2100	2100
https://www.discounttire.com/store/ut/holladay/s/1262	1262
https://www.discounttire.com/store/ut/riverton/s/1635	1635
https://www.discounttire.com/store/ut/salt-lake-city/s/1256	1256
https://www.discounttire.com/store/ut/taylorsville/s/1260	1260
https://www.discounttire.com/store/va/newport-news/s/2074	2074
https://www.discounttire.com/store/va/williamsburg/s/2091	2091
https://www.discounttire.com/store/az/flagstaff/s/1002	1002
https://www.discounttire.com/store/az/scottsdale/s/1022	1022
https://www.discounttire.com/store/az/show-low/s/1871	1871
https://www.discounttire.com/store/co/aurora/s/1667	1667
https://www.discounttire.com/store/co/denver/s/1101	1101
https://www.discounttire.com/store/co/durango/s/2002	2002
https://www.discounttire.com/store/co/federal-heights/s/1099	1099
https://www.discounttire.com/store/co/littleton/s/1092	1092
https://www.discounttire.com/store/co/monument/s/1848	1848
https://www.discounttire.com/store/co/northglenn/s/1309	1309
https://www.discounttire.com/store/co/pueblo/s/2175	2175
https://www.discounttire.com/store/co/wheat-ridge/s/1097	1097
https://www.discounttire.com/store/fl/weston/s/2351	2351
https://www.discounttire.com/store/il/algonquin/s/1414	1414
https://www.discounttire.com/store/il/carpentersville/s/1772	1772
https://www.discounttire.com/store/il/elgin/s/1507	1507
https://www.discounttire.com/store/il/homer-glen/s/1553	1553
https://www.discounttire.com/store/in/evansville/s/1837	1837
https://www.discounttire.com/store/in/fort-wayne/s/1299	1299
https://www.discounttire.com/store/in/fort-wayne/s/1701	1701
https://www.discounttire.com/store/in/indianapolis/s/1292	1292
https://www.discounttire.com/store/in/indianapolis/s/1322	1322
https://www.discounttire.com/store/in/merrillville/s/1583	1583
https://www.discounttire.com/store/in/warsaw/s/2014	2014
https://www.discounttire.com/store/mi/brighton/s/1835	1835
https://www.discounttire.com/store/mi/canton/s/1135	1135
https://www.discounttire.com/store/mi/center-line/s/1285	1285
https://www.discounttire.com/store/mi/commerce-township/s/1404	1404
https://www.discounttire.com/store/mi/flint/s/1140	1140
https://www.discounttire.com/store/mi/howell/s/1446	1446
https://www.discounttire.com/store/mi/macomb/s/1405	1405
https://www.discounttire.com/store/mi/new-hudson/s/1627	1627
https://www.discounttire.com/store/mi/saginaw/s/1153	1153
https://www.discounttire.com/store/mi/troy/s/1522	1522
https://www.discounttire.com/store/mn/brooklyn-park/s/1884	1884
https://www.discounttire.com/store/mn/burnsville/s/1494	1494
https://www.discounttire.com/store/mn/eagan/s/1919	1919
https://www.discounttire.com/store/mn/inver-grove-heights/s/1733	1733
https://www.discounttire.com/store/mn/plymouth/s/1496	1496
https://www.discounttire.com/store/mn/rochester/s/1726	1726
https://www.discounttire.com/store/nm/albuquerque/s/2221	2221
https://www.discounttire.com/store/nm/santa-fe/s/1743	1743
https://www.discounttire.com/store/oh/cincinnati/s/2040	2040
https://www.discounttire.com/store/oh/cincinnati/s/2072	2072
https://www.discounttire.com/store/oh/lima/s/2121	2121
https://www.discounttire.com/store/oh/parma-heights/s/1978	1978
https://www.discounttire.com/store/tx/houston/s/2278	2278
https://www.discounttire.com/store/va/virginia-beach/s/2066	2066
https://www.discounttire.com/store/wa/bellingham/s/2021	2021
https://www.discounttire.com/store/wa/burlington/s/1724	1724
https://www.discounttire.com/store/wa/kirkland/s/1269	1269
https://www.discounttire.com/store/wa/lakewood/s/1272	1272
https://www.discounttire.com/store/wa/spokane-valley/s/1263	1263
https://www.discounttire.com/store/wa/spokane/s/1264	1264
https://www.discounttire.com/store/wi/green-bay/s/2053	2053
https://www.discounttire.com/store/wi/janesville/s/2084	2084
https://www.discounttire.com/store/wi/madison/s/2141	2141
https://www.discounttire.com/store/wi/waukesha/s/1900	1900
https://www.discounttire.com/store/wy/cheyenne/s/1815	1815
https://www.discounttire.com/store/ar/bentonville/s/2281	2281
https://www.discounttire.com/store/co/fort-collins/s/1949	1949
https://www.discounttire.com/store/co/lafayette/s/1826	1826
https://www.discounttire.com/store/co/loveland/s/1756	1756
https://www.discounttire.com/store/ia/fort-dodge/s/2266	2266
https://www.discounttire.com/store/il/naperville/s/1534	1534
https://www.discounttire.com/store/il/oak-lawn/s/1702	1702
https://www.discounttire.com/store/il/westmont/s/1738	1738
https://www.discounttire.com/store/mn/woodbury/s/2019	2019
https://www.discounttire.com/store/mo/farmington/s/2288	2288
https://www.discounttire.com/store/oh/columbus/s/1421	1421
https://www.discounttire.com/store/tx/san-antonio/s/2245	2245
https://www.discounttire.com/store/wv/martinsburg/s/2259	2259
https://www.discounttire.com/store/il/o-fallon/s/2307	2307
https://www.discounttire.com/store/wi/racine/s/2264	2264
https://www.discounttire.com/store/nc/new-bern/s/2393	2393
https://www.discounttire.com/store/tx/houston/s/2380	2380
https://www.discounttire.com/store/al/foley/s/2377	2377
https://www.discounttire.com/store/ar/springdale/s/2374	2374
https://www.discounttire.com/store/fl/saint-cloud/s/2392	2392
https://www.discounttire.com/store/la/baton-rouge/s/2398	2398
https://www.discounttire.com/store/la/lake-charles/s/2368	2368
https://www.discounttire.com/store/fl/fort-myers/s/2334	2334
https://www.discounttire.com/store/nc/kernersville/s/2375	2375
https://www.discounttire.com/store/tx/hudson-oaks/s/2303	2303
https://www.discounttire.com/store/tx/montgomery/s/2367	2367
https://www.discounttire.com/store/tx/seguin/s/2366	2366
https://www.discounttire.com/store/co/longmont/s/2431	2431
https://www.discounttire.com/store/il/peoria/s/2415	2415
https://www.discounttire.com/store/pa/altoona/s/2348	2348
https://www.discounttire.com/store/co/thornton/s/2243	2243
https://www.discounttire.com/store/mo/wentzville/s/2318	2318
https://www.discounttire.com/store/or/albany/s/2311	2311
https://www.discounttire.com/store/wa/poulsbo/s/2342	2342
https://www.discounttire.com/store/ks/topeka/s/2360	2360
https://www.discounttire.com/store/mi/mt-pleasant/s/2371	2371
https://www.discounttire.com/store/ar/benton/s/2150	2150
https://www.discounttire.com/store/ar/fayetteville/s/2008	2008
https://www.discounttire.com/store/ar/fort-smith/s/2067	2067
https://www.discounttire.com/store/ar/rogers/s/2208	2208
https://www.discounttire.com/store/ca/el-centro/s/1841	1841
https://www.discounttire.com/store/ca/encinitas/s/1073	1073
https://www.discounttire.com/store/ca/escondido/s/1077	1077
https://www.discounttire.com/store/ca/oceanside/s/1081	1081
https://www.discounttire.com/store/ca/oceanside/s/1083	1083
https://www.discounttire.com/store/ca/poway/s/1074	1074
https://www.discounttire.com/store/ca/san-diego/s/1075	1075
https://www.discounttire.com/store/ca/san-diego/s/1082	1082
https://www.discounttire.com/store/ca/san-diego/s/1872	1872
https://www.discounttire.com/store/co/parker/s/2174	2174
https://www.discounttire.com/store/fl/greenacres/s/2143	2143
https://www.discounttire.com/store/fl/jacksonville/s/1729	1729
https://www.discounttire.com/store/fl/jacksonville/s/2098	2098
https://www.discounttire.com/store/fl/lake-city/s/2026	2026
https://www.discounttire.com/store/fl/mount-dora/s/2170	2170
https://www.discounttire.com/store/fl/orange-park/s/1113	1113
https://www.discounttire.com/store/fl/ormond-beach/s/1464	1464
https://www.discounttire.com/store/fl/pensacola/s/2240	2240
https://www.discounttire.com/store/fl/saint-johns/s/2241	2241
https://www.discounttire.com/store/fl/wellington/s/2105	2105
https://www.discounttire.com/store/ga/alpharetta/s/1585	1585
https://www.discounttire.com/store/ga/chamblee/s/1527	1527
https://www.discounttire.com/store/ga/cumming/s/1677	1677
https://www.discounttire.com/store/ga/kennesaw/s/2225	2225
https://www.discounttire.com/store/ga/lawrenceville/s/1746	1746
https://www.discounttire.com/store/ga/loganville/s/1849	1849
https://www.discounttire.com/store/ga/smyrna/s/1963	1963
https://www.discounttire.com/store/ga/suwanee/s/2103	2103
https://www.discounttire.com/store/ga/valdosta/s/2216	2216
https://www.discounttire.com/store/il/naperville/s/7025	7025
https://www.discounttire.com/store/la/prairieville/s/2058	2058
https://www.discounttire.com/store/mi/gaylord/s/2251	2251
https://www.discounttire.com/store/mo/branson/s/2299	2299
https://www.discounttire.com/store/mo/springfield/s/2062	2062
https://www.discounttire.com/store/nc/cary/s/1647	1647
https://www.discounttire.com/store/nc/charlotte/s/1478	1478
https://www.discounttire.com/store/nc/durham/s/1708	1708
https://www.discounttire.com/store/nc/durham/s/1767	1767
https://www.discounttire.com/store/nc/fayetteville/s/2173	2173
https://www.discounttire.com/store/nc/greensboro/s/1502	1502
https://www.discounttire.com/store/nc/winston-salem/s/1581	1581
https://www.discounttire.com/store/nv/las-vegas/s/1170	1170
https://www.discounttire.com/store/nv/las-vegas/s/1171	1171
https://www.discounttire.com/store/nv/las-vegas/s/1394	1394
https://www.discounttire.com/store/nv/las-vegas/s/1648	1648
https://www.discounttire.com/store/nv/north-las-vegas/s/2244	2244
https://www.discounttire.com/store/ok/norman/s/1887	1887
https://www.discounttire.com/store/ok/oklahoma-city/s/1865	1865
https://www.discounttire.com/store/sc/aiken/s/2118	2118
https://www.discounttire.com/store/sc/columbia/s/1840	1840
https://www.discounttire.com/store/sc/lexington/s/1915	1915
https://www.discounttire.com/store/sc/myrtle-beach/s/2183	2183
https://www.discounttire.com/store/sc/rock-hill/s/1616	1616
https://www.discounttire.com/store/sc/spartanburg/s/1681	1681
https://www.discounttire.com/store/sc/sumter/s/2188	2188
https://www.discounttire.com/store/tn/alcoa/s/1883	1883
https://www.discounttire.com/store/tn/clarksville/s/1982	1982
https://www.discounttire.com/store/tn/farragut/s/1943	1943
https://www.discounttire.com/store/tn/murfreesboro/s/2093	2093
https://www.discounttire.com/store/tx/alvin/s/2242	2242
https://www.discounttire.com/store/va/colonial-heights/s/2125	2125
https://www.discounttire.com/store/va/north-chesterfield/s/2215	2215
https://www.discounttire.com/store/wi/oshkosh/s/2232	2232
https://www.discounttire.com/store/wy/gillette/s/2270	2270
https://www.discounttire.com/store/az/chandler/s/1024	1024
https://www.discounttire.com/store/az/glendale/s/1016	1016
https://www.discounttire.com/store/az/glendale/s/1517	1517
https://www.discounttire.com/store/az/kingman/s/1941	1941
https://www.discounttire.com/store/az/peoria/s/1687	1687
https://www.discounttire.com/store/az/prescott/s/1441	1441
https://www.discounttire.com/store/az/scottsdale/s/1009	1009
https://www.discounttire.com/store/az/tempe/s/1007	1007
https://www.discounttire.com/store/az/tucson/s/1867	1867
https://www.discounttire.com/store/az/yuma/s/2010	2010
https://www.discounttire.com/store/fl/apopka/s/1291	1291
https://www.discounttire.com/store/nm/albuquerque/s/1161	1161
https://www.discounttire.com/store/nm/albuquerque/s/1354	1354
https://www.discounttire.com/store/nm/albuquerque/s/1467	1467
https://www.discounttire.com/store/nm/albuquerque/s/1492	1492
https://www.discounttire.com/store/nm/clovis/s/1638	1638
https://www.discounttire.com/store/nm/hobbs/s/1774	1774
https://www.discounttire.com/store/nm/los-lunas/s/1671	1671
https://www.discounttire.com/store/sc/fort-mill/s/1937	1937
https://www.discounttire.com/store/sc/indian-land/s/1882	1882
https://www.discounttire.com/store/tn/brentwood/s/1765	1765
https://www.discounttire.com/store/tx/abilene/s/2041	2041
https://www.discounttire.com/store/tx/amarillo/s/1255	1255
https://www.discounttire.com/store/tx/arlington/s/1443	1443
https://www.discounttire.com/store/tx/austin/s/1178	1178
https://www.discounttire.com/store/tx/austin/s/1558	1558
https://www.discounttire.com/store/tx/bastrop/s/1629	1629
https://www.discounttire.com/store/tx/beaumont/s/1674	1674
https://www.discounttire.com/store/tx/boerne/s/2012	2012
https://www.discounttire.com/store/tx/copperas-cove/s/1816	1816
https://www.discounttire.com/store/tx/corpus-christi/s/1863	1863
https://www.discounttire.com/store/tx/dallas/s/1202	1202
https://www.discounttire.com/store/tx/dallas/s/1956	1956
https://www.discounttire.com/store/tx/eagle-pass/s/2087	2087
https://www.discounttire.com/store/tx/edinburg/s/1722	1722
https://www.discounttire.com/store/tx/el-paso/s/1557	1557
https://www.discounttire.com/store/tx/fort-worth/s/1402	1402
https://www.discounttire.com/store/tx/friendswood/s/1812	1812
https://www.discounttire.com/store/tx/garland/s/1187	1187
https://www.discounttire.com/store/tx/grand-prairie/s/1356	1356
https://www.discounttire.com/store/tx/grapevine/s/1568	1568
https://www.discounttire.com/store/tx/greenville/s/1787	1787
https://www.discounttire.com/store/tx/houston/s/1213	1213
https://www.discounttire.com/store/tx/houston/s/1215	1215
https://www.discounttire.com/store/tx/houston/s/1220	1220
https://www.discounttire.com/store/tx/houston/s/1623	1623
https://www.discounttire.com/store/tx/houston/s/1809	1809
https://www.discounttire.com/store/tx/keller/s/1617	1617
https://www.discounttire.com/store/tx/leon-valley/s/1254	1254
https://www.discounttire.com/store/tx/lubbock/s/1244	1244
https://www.discounttire.com/store/tx/midland/s/2201	2201
https://www.discounttire.com/store/tx/mission/s/2088	2088
https://www.discounttire.com/store/tx/missouri-city/s/2070	2070
https://www.discounttire.com/store/tx/mount-pleasant/s/1986	1986
https://www.discounttire.com/store/tx/new-braunfels/s/1889	1889
https://www.discounttire.com/store/tx/odessa/s/1318	1318
https://www.discounttire.com/store/tx/odessa/s/1959	1959
https://www.discounttire.com/store/tx/palestine/s/2190	2190
https://www.discounttire.com/store/tx/san-antonio/s/1252	1252
https://www.discounttire.com/store/tx/san-antonio/s/1408	1408
https://www.discounttire.com/store/tx/san-antonio/s/1432	1432
https://www.discounttire.com/store/tx/san-antonio/s/1562	1562
https://www.discounttire.com/store/tx/san-antonio/s/1682	1682
https://www.discounttire.com/store/tx/sherman/s/1653	1653
https://www.discounttire.com/store/tx/texarkana/s/1680	1680
https://www.discounttire.com/store/tx/victoria/s/2052	2052
https://www.discounttire.com/store/tx/weatherford/s/1652	1652
https://www.discounttire.com/store/va/chesapeake/s/2124	2124
https://www.discounttire.com/store/va/virginia-beach/s/2207	2207
https://www.discounttire.com/store/az/mesa/s/1659	1659
https://www.discounttire.com/store/az/tucson/s/1035	1035
https://www.discounttire.com/store/az/tucson/s/1036	1036
https://www.discounttire.com/store/ia/cedar-rapids/s/2114	2114
https://www.discounttire.com/store/ia/sioux-city/s/2076	2076
https://www.discounttire.com/store/id/garden-city/s/2060	2060
https://www.discounttire.com/store/id/nampa/s/1926	1926
https://www.discounttire.com/store/id/pocatello/s/2048	2048
https://www.discounttire.com/store/il/rockford/s/1427	1427
https://www.discounttire.com/store/ks/olathe/s/1989	1989
https://www.discounttire.com/store/mo/liberty/s/1935	1935
https://www.discounttire.com/store/ne/omaha/s/1932	1932
https://www.discounttire.com/store/nv/reno/s/1947	1947
https://www.discounttire.com/store/or/hillsboro/s/1634	1634
https://www.discounttire.com/store/tx/cypress/s/1596	1596
https://www.discounttire.com/store/tx/houston/s/2101	2101
https://www.discounttire.com/store/tx/spring/s/1657	1657
https://www.discounttire.com/store/tx/wylie/s/2068	2068
https://www.discounttire.com/store/ut/layton/s/1413	1413
https://www.discounttire.com/store/ut/layton/s/1542	1542
https://www.discounttire.com/store/ut/ogden/s/1789	1789
https://www.discounttire.com/store/ut/riverdale/s/1602	1602
https://www.discounttire.com/store/ut/w-valley-city/s/1646	1646
https://www.discounttire.com/store/ut/west-jordan/s/1447	1447
https://www.discounttire.com/store/wa/sequim/s/1827	1827
https://www.discounttire.com/store/al/huntsville/s/2268	2268
https://www.discounttire.com/store/ar/searcy/s/2271	2271
https://www.discounttire.com/store/co/arvada/s/1514	1514
https://www.discounttire.com/store/co/aurora/s/1089	1089
https://www.discounttire.com/store/co/aurora/s/1094	1094
https://www.discounttire.com/store/co/brighton/s/1851	1851
https://www.discounttire.com/store/co/broomfield/s/1465	1465
https://www.discounttire.com/store/co/castle-rock/s/1664	1664
https://www.discounttire.com/store/co/centennial/s/1307	1307
https://www.discounttire.com/store/co/centennial/s/1466	1466
https://www.discounttire.com/store/co/colorado-springs/s/1110	1110
https://www.discounttire.com/store/co/colorado-springs/s/1430	1430
https://www.discounttire.com/store/co/denver/s/1091	1091
https://www.discounttire.com/store/co/denver/s/1103	1103
https://www.discounttire.com/store/co/glenwood-springs/s/2004	2004
https://www.discounttire.com/store/co/grand-junction/s/1107	1107
https://www.discounttire.com/store/co/grand-junction/s/2110	2110
https://www.discounttire.com/store/co/longmont/s/1566	1566
https://www.discounttire.com/store/ga/dawsonville/s/2287	2287
https://www.discounttire.com/store/il/joliet/s/1536	1536
https://www.discounttire.com/store/il/round-lake-beach/s/1862	1862
https://www.discounttire.com/store/in/columbus/s/2195	2195
https://www.discounttire.com/store/in/indianapolis/s/1301	1301
https://www.discounttire.com/store/in/indianapolis/s/2017	2017
https://www.discounttire.com/store/in/indianapolis/s/2152	2152
https://www.discounttire.com/store/in/muncie/s/1739	1739
https://www.discounttire.com/store/in/noblesville/s/1624	1624
https://www.discounttire.com/store/in/plainfield/s/1444	1444
https://www.discounttire.com/store/mi/adrian/s/1822	1822
https://www.discounttire.com/store/mi/bay-city/s/1156	1156
https://www.discounttire.com/store/mi/dearborn/s/1412	1412
https://www.discounttire.com/store/mi/fenton/s/1423	1423
https://www.discounttire.com/store/mi/fort-gratiot/s/1282	1282
https://www.discounttire.com/store/mi/grand-rapids/s/1142	1142
https://www.discounttire.com/store/mi/grand-rapids/s/1143	1143
https://www.discounttire.com/store/mi/livonia/s/1136	1136
https://www.discounttire.com/store/mi/norton-shores/s/1146	1146
https://www.discounttire.com/store/mi/rochester-hills/s/1442	1442
https://www.discounttire.com/store/mi/shelby-township/s/1740	1740
https://www.discounttire.com/store/mi/taylor/s/1133	1133
https://www.discounttire.com/store/mi/traverse-city/s/1429	1429
https://www.discounttire.com/store/mi/white-lake/s/2015	2015
https://www.discounttire.com/store/mi/wyoming/s/1144	1144
https://www.discounttire.com/store/mn/baxter/s/1928	1928
https://www.discounttire.com/store/mn/columbia-heights/s/1588	1588
https://www.discounttire.com/store/mn/coon-rapids/s/1640	1640
https://www.discounttire.com/store/mn/duluth/s/1836	1836
https://www.discounttire.com/store/mn/mankato/s/1691	1691
https://www.discounttire.com/store/mn/maple-grove/s/1893	1893
https://www.discounttire.com/store/mn/rochester/s/1615	1615
https://www.discounttire.com/store/mn/rogers/s/1692	1692
https://www.discounttire.com/store/mn/shakopee/s/1587	1587
https://www.discounttire.com/store/oh/dublin/s/1488	1488
https://www.discounttire.com/store/oh/grove-city/s/1641	1641
https://www.discounttire.com/store/oh/hamilton/s/2031	2031
https://www.discounttire.com/store/oh/hilliard/s/1578	1578
https://www.discounttire.com/store/wa/auburn/s/1683	1683
https://www.discounttire.com/store/wa/bellingham/s/2129	2129
https://www.discounttire.com/store/wa/bonney-lake/s/1838	1838
https://www.discounttire.com/store/wa/federal-way/s/1855	1855
https://www.discounttire.com/store/wa/lacey/s/1276	1276
https://www.discounttire.com/store/wa/marysville/s/1759	1759
https://www.discounttire.com/store/wa/puyallup/s/1449	1449
https://www.discounttire.com/store/wa/redmond/s/1925	1925
https://www.discounttire.com/store/wa/seattle/s/1273	1273
https://www.discounttire.com/store/wa/vancouver/s/1905	1905
https://www.discounttire.com/store/al/dothan/s/2324	2324
https://www.discounttire.com/store/al/hoover/s/2353	2353
https://www.discounttire.com/store/ia/mason-city/s/2234	2234
https://www.discounttire.com/store/il/hanover-park/s/1961	1961
https://www.discounttire.com/store/il/naperville/s/1339	1339
https://www.discounttire.com/store/il/naperville/s/1564	1564
https://www.discounttire.com/store/il/palatine/s/1459	1459
https://www.discounttire.com/store/il/schaumburg/s/1954	1954
https://www.discounttire.com/store/ks/wichita/s/2238	2238
https://www.discounttire.com/store/mn/maplewood/s/1498	1498
https://www.discounttire.com/store/oh/lewis-center/s/1520	1520
https://www.discounttire.com/store/tx/round-rock/s/2285	2285
https://www.discounttire.com/store/az/maricopa/s/2296	2296
https://www.discounttire.com/store/mi/marquette/s/2269	2269
https://www.discounttire.com/store/mo/florissant/s/2293	2293
https://www.discounttire.com/store/al/opelika/s/2404	2404
https://www.discounttire.com/store/az/phoenix/s/2363	2363
https://www.discounttire.com/store/fl/lake-mary/s/2340	2340
https://www.discounttire.com/store/ga/albany/s/2369	2369
https://www.discounttire.com/store/la/denham-springs/s/2249	2249
https://www.discounttire.com/store/nc/fuquay-varina/s/2357	2357
https://www.discounttire.com/store/fl/titusville/s/2332	2332
https://www.discounttire.com/store/nc/concord/s/2364	2364
https://www.discounttire.com/store/sc/easley/s/2344	2344
https://www.discounttire.com/store/va/christiansburg/s/2402	2402
https://www.discounttire.com/store/va/fredericksburg/s/2397	2397
https://www.discounttire.com/store/wi/eau-claire/s/2346	2346
https://www.discounttire.com/store/co/fountain/s/2297	2297
https://www.discounttire.com/store/co/greeley/s/2168	2168
https://www.discounttire.com/store/ms/olive-branch/s/2394	2394
https://www.discounttire.com/store/oh/huber-heights/s/2386	2386
https://www.discounttire.com/store/sd/rapid-city/s/2206	2206
https://www.discounttire.com/store/tn/knoxville/s/2298	2298
https://www.discounttire.com/store/ia/ankeny/s/2355	2355
https://www.discounttire.com/store/ks/lenexa/s/2322	2322
https://www.discounttire.com/store/wi/appleton/s/2339	2339
https://www.discounttire.com/store/wy/casper/s/2316	2316
https://www.discounttire.com/store/il/melrose-park/s/2310	2310
https://www.discounttire.com/store/ar/conway/s/2184	2184
https://www.discounttire.com/store/ca/el-cajon/s/1069	1069
https://www.discounttire.com/store/ca/el-cajon/s/1417	1417
https://www.discounttire.com/store/ca/lemon-grove/s/1080	1080
https://www.discounttire.com/store/ca/san-diego/s/1079	1079
https://www.discounttire.com/store/ca/san-diego/s/1549	1549
https://www.discounttire.com/store/ca/vista/s/1078	1078
https://www.discounttire.com/store/fl/daytona-beach/s/1112	1112
https://www.discounttire.com/store/fl/jacksonville/s/1297	1297
https://www.discounttire.com/store/fl/jacksonville/s/1717	1717
https://www.discounttire.com/store/fl/kissimmee/s/1114	1114
https://www.discounttire.com/store/fl/lakeland/s/1923	1923
https://www.discounttire.com/store/fl/orange-park/s/1582	1582
https://www.discounttire.com/store/fl/orlando/s/1119	1119
https://www.discounttire.com/store/fl/orlando/s/1550	1550
https://www.discounttire.com/store/fl/orlando/s/1614	1614
https://www.discounttire.com/store/fl/pensacola/s/1902	1902
https://www.discounttire.com/store/fl/st-augustine/s/1953	1953
https://www.discounttire.com/store/fl/tallahassee/s/1353	1353
https://www.discounttire.com/store/fl/tallahassee/s/1400	1400
https://www.discounttire.com/store/ga/buford/s/1806	1806
https://www.discounttire.com/store/ga/cartersville/s/2153	2153
https://www.discounttire.com/store/ga/fayetteville/s/2252	2252
https://www.discounttire.com/store/ga/fort-oglethorpe/s/2112	2112
https://www.discounttire.com/store/ga/lilburn/s/2126	2126
https://www.discounttire.com/store/ga/macon/s/1803	1803
https://www.discounttire.com/store/ga/savannah/s/2224	2224
https://www.discounttire.com/store/ga/warner-robins/s/2169	2169
https://www.discounttire.com/store/mo/springfield/s/2157	2157
https://www.discounttire.com/store/nc/cary/s/1580	1580
https://www.discounttire.com/store/nc/charlotte/s/1457	1457
https://www.discounttire.com/store/nc/elizabeth-city/s/2196	2196
https://www.discounttire.com/store/nc/greenville/s/2108	2108
https://www.discounttire.com/store/nc/hickory/s/1845	1845
https://www.discounttire.com/store/nc/knightdale/s/1643	1643
https://www.discounttire.com/store/nc/monroe/s/1620	1620
https://www.discounttire.com/store/ne/omaha/s/1946	1946
https://www.discounttire.com/store/nv/henderson/s/1300	1300
https://www.discounttire.com/store/nv/las-vegas/s/1452	1452
https://www.discounttire.com/store/nv/las-vegas/s/1471	1471
https://www.discounttire.com/store/ok/bixby/s/2149	2149
https://www.discounttire.com/store/ok/collinsville/s/1966	1966
https://www.discounttire.com/store/ok/oklahoma-city/s/1782	1782
https://www.discounttire.com/store/ok/oklahoma-city/s/1873	1873
https://www.discounttire.com/store/ok/shawnee/s/2137	2137
https://www.discounttire.com/store/ok/tulsa/s/1929	1929
https://www.discounttire.com/store/ok/tulsa/s/2128	2128
https://www.discounttire.com/store/ok/tulsa/s/2219	2219
https://www.discounttire.com/store/sc/anderson/s/1974	1974
https://www.discounttire.com/store/sc/beaufort/s/2135	2135
https://www.discounttire.com/store/sc/columbia/s/2051	2051
https://www.discounttire.com/store/tn/chattanooga/s/2155	2155
https://www.discounttire.com/store/tn/cleveland/s/1980	1980
https://www.discounttire.com/store/tn/hendersonville/s/1780	1780
https://www.discounttire.com/store/tn/jackson/s/2192	2192
https://www.discounttire.com/store/tn/johnson-city/s/2044	2044
https://www.discounttire.com/store/tn/kingsport/s/2176	2176
https://www.discounttire.com/store/tn/lebanon/s/1805	1805
https://www.discounttire.com/store/tn/mount-juliet/s/1755	1755
https://www.discounttire.com/store/tn/murfreesboro/s/1748	1748
https://www.discounttire.com/store/tn/smyrna/s/1831	1831
https://www.discounttire.com/store/va/bristol/s/2162	2162
https://www.discounttire.com/store/az/avondale/s/1721	1721
https://www.discounttire.com/store/az/bullhead-city/s/2117	2117
https://www.discounttire.com/store/az/gilbert/s/1418	1418
https://www.discounttire.com/store/az/mesa/s/1005	1005
https://www.discounttire.com/store/az/mesa/s/1015	1015
https://www.discounttire.com/store/az/peoria/s/1025	1025
https://www.discounttire.com/store/az/phoenix/s/1003	1003
https://www.discounttire.com/store/az/phoenix/s/1010	1010
https://www.discounttire.com/store/az/phoenix/s/1011	1011
https://www.discounttire.com/store/az/phoenix/s/1019	1019
https://www.discounttire.com/store/az/phoenix/s/1020	1020
https://www.discounttire.com/store/az/phoenix/s/1028	1028
https://www.discounttire.com/store/az/phoenix/s/1469	1469
https://www.discounttire.com/store/az/surprise/s/1504	1504
https://www.discounttire.com/store/az/tolleson/s/2104	2104
https://www.discounttire.com/store/az/tucson/s/2122	2122
https://www.discounttire.com/store/az/yuma/s/1295	1295
https://www.discounttire.com/store/nm/albuquerque/s/1160	1160
https://www.discounttire.com/store/nm/albuquerque/s/1162	1162
https://www.discounttire.com/store/nm/rio-rancho/s/1747	1747
https://www.discounttire.com/store/tx/abilene/s/1523	1523
https://www.discounttire.com/store/tx/amarillo/s/1936	1936
https://www.discounttire.com/store/tx/arlington/s/1191	1191
https://www.discounttire.com/store/tx/arlington/s/1454	1454
https://www.discounttire.com/store/tx/austin/s/1366	1366
https://www.discounttire.com/store/tx/austin/s/1473	1473
https://www.discounttire.com/store/tx/baytown/s/1675	1675
https://www.discounttire.com/store/tx/bee-cave/s/1713	1713
https://www.discounttire.com/store/tx/bellmead/s/1727	1727
https://www.discounttire.com/store/tx/bryan/s/1916	1916
https://www.discounttire.com/store/tx/cedar-hill/s/1584	1584
https://www.discounttire.com/store/tx/cedar-park/s/1590	1590
https://www.discounttire.com/store/tx/college-station/s/1233	1233
https://www.discounttire.com/store/tx/college-station/s/2000	2000
https://www.discounttire.com/store/tx/conroe/s/1232	1232
https://www.discounttire.com/store/tx/corpus-christi/s/1179	1179
https://www.discounttire.com/store/tx/dallas/s/1183	1183
https://www.discounttire.com/store/tx/dallas/s/1190	1190
https://www.discounttire.com/store/tx/dallas/s/1198	1198
https://www.discounttire.com/store/tx/dallas/s/1281	1281
https://www.discounttire.com/store/tx/dallas/s/1833	1833
https://www.discounttire.com/store/tx/edinburg/s/2094	2094
https://www.discounttire.com/store/tx/el-paso/s/2127	2127
https://www.discounttire.com/store/tx/flower-mound/s/1431	1431
https://www.discounttire.com/store/tx/fort-worth/s/1563	1563
https://www.discounttire.com/store/tx/georgetown/s/1694	1694
https://www.discounttire.com/store/tx/grapevine/s/1367	1367
https://www.discounttire.com/store/tx/harker-heights/s/1852	1852
https://www.discounttire.com/store/tx/houston/s/1214	1214
https://www.discounttire.com/store/tx/houston/s/1228	1228
https://www.discounttire.com/store/tx/houston/s/1230	1230
https://www.discounttire.com/store/tx/houston/s/1240	1240
https://www.discounttire.com/store/tx/irving/s/1368	1368
https://www.discounttire.com/store/tx/lake-jackson/s/1238	1238
https://www.discounttire.com/store/tx/lubbock/s/1567	1567
https://www.discounttire.com/store/tx/marble-falls/s/1910	1910
https://www.discounttire.com/store/tx/mckinney/s/1382	1382
https://www.discounttire.com/store/tx/mesquite/s/1196	1196
https://www.discounttire.com/store/tx/mesquite/s/1199	1199
https://www.discounttire.com/store/tx/mission/s/2123	2123
https://www.discounttire.com/store/tx/new-braunfels/s/1433	1433
https://www.discounttire.com/store/tx/north--richland-hills/s/1569	1569
https://www.discounttire.com/store/tx/plano/s/1186	1186
https://www.discounttire.com/store/tx/port-arthur/s/1565	1565
https://www.discounttire.com/store/tx/roanoke/s/1909	1909
https://www.discounttire.com/store/tx/rockwall/s/1386	1386
https://www.discounttire.com/store/tx/round-rock/s/1406	1406
https://www.discounttire.com/store/tx/rowlett/s/1970	1970
https://www.discounttire.com/store/tx/sachse/s/1723	1723
https://www.discounttire.com/store/tx/san-antonio/s/1313	1313
https://www.discounttire.com/store/tx/san-antonio/s/1489	1489
https://www.discounttire.com/store/tx/san-antonio/s/1858	1858
https://www.discounttire.com/store/tx/san-antonio/s/2131	2131
https://www.discounttire.com/store/tx/san-marcos/s/1474	1474
https://www.discounttire.com/store/tx/spring-branch/s/2092	2092
https://www.discounttire.com/store/tx/sugar-land/s/2056	2056
https://www.discounttire.com/store/tx/temple/s/1706	1706
https://www.discounttire.com/store/tx/terrell/s/2043	2043
https://www.discounttire.com/store/tx/texas-city/s/1231	1231
https://www.discounttire.com/store/tx/victoria/s/1860	1860
https://www.discounttire.com/store/tx/waco/s/1305	1305
https://www.discounttire.com/store/tx/webster/s/1226	1226
https://www.discounttire.com/store/tx/weslaco/s/1749	1749
https://www.discounttire.com/store/az/apache-junction/s/2154	2154
https://www.discounttire.com/store/az/oro-valley/s/1628	1628
https://www.discounttire.com/store/az/phoenix/s/1668	1668
https://www.discounttire.com/store/az/phoenix/s/2132	2132
https://www.discounttire.com/store/az/surprise/s/1825	1825
https://www.discounttire.com/store/az/tucson/s/1032	1032
https://www.discounttire.com/store/ia/clive/s/2073	2073
https://www.discounttire.com/store/ia/coralville/s/1965	1965
https://www.discounttire.com/store/ia/des-moines/s/2038	2038
https://www.discounttire.com/store/id/hayden/s/1791	1791
https://www.discounttire.com/store/il/machesney-park/s/1864	1864
https://www.discounttire.com/store/ks/overland-park/s/2042	2042
https://www.discounttire.com/store/mi/farmington-hills/s/1130	1130
https://www.discounttire.com/store/mo/kansas-city/s/1957	1957
https://www.discounttire.com/store/nv/carson-city/s/1886	1886
https://www.discounttire.com/store/nv/sparks/s/1823	1823
https://www.discounttire.com/store/oh/aurora/s/2191	2191
https://www.discounttire.com/store/or/eugene/s/1174	1174
https://www.discounttire.com/store/or/medford/s/2069	2069
https://www.discounttire.com/store/or/salem/s/1396	1396
https://www.discounttire.com/store/or/wilsonville/s/1897	1897
https://www.discounttire.com/store/tx/conroe/s/1435	1435
https://www.discounttire.com/store/tx/conroe/s/1751	1751
https://www.discounttire.com/store/tx/katy/s/1750	1750
https://www.discounttire.com/store/tx/mckinney/s/1605	1605
https://www.discounttire.com/store/tx/missouri-city/s/1950	1950
https://www.discounttire.com/store/tx/plano/s/1422	1422
https://www.discounttire.com/store/tx/plano/s/1618	1618
https://www.discounttire.com/store/tx/richmond/s/1898	1898
https://www.discounttire.com/store/tx/sugar-land/s/1810	1810
https://www.discounttire.com/store/ut/american-fork/s/1626	1626
https://www.discounttire.com/store/ut/murray/s/1401	1401
https://www.discounttire.com/store/ut/provo/s/1744	1744
https://www.discounttire.com/store/ut/sandy/s/1758	1758
https://www.discounttire.com/store/ut/saratoga-springs/s/2082	2082
https://www.discounttire.com/store/ut/spanish-fork/s/2138	2138
https://www.discounttire.com/store/va/virginia-beach/s/2065	2065
https://www.discounttire.com/store/az/flagstaff/s/1425	1425
https://www.discounttire.com/store/co/aurora/s/1090	1090
https://www.discounttire.com/store/co/denver/s/1397	1397
https://www.discounttire.com/store/co/highlands-ranch/s/1102	1102
https://www.discounttire.com/store/co/highlands-ranch/s/1684	1684
https://www.discounttire.com/store/co/lakewood/s/1096	1096
https://www.discounttire.com/store/co/littleton/s/1106	1106
https://www.discounttire.com/store/co/littleton/s/2086	2086
https://www.discounttire.com/store/co/pueblo/s/1109	1109
https://www.discounttire.com/store/co/thornton/s/1515	1515
https://www.discounttire.com/store/il/bolingbrook/s/1577	1577
https://www.discounttire.com/store/il/bourbonnais/s/1993	1993
https://www.discounttire.com/store/il/crestwood/s/1395	1395
https://www.discounttire.com/store/in/clarksville/s/2181	2181
https://www.discounttire.com/store/in/elkhart/s/1121	1121
https://www.discounttire.com/store/in/evansville/s/1997	1997
https://www.discounttire.com/store/in/fishers/s/1846	1846
https://www.discounttire.com/store/in/fort-wayne/s/2226	2226
https://www.discounttire.com/store/in/highland/s/1707	1707
https://www.discounttire.com/store/in/indianapolis/s/1337	1337
https://www.discounttire.com/store/in/lafayette/s/1763	1763
https://www.discounttire.com/store/in/south-bend/s/1120	1120
https://www.discounttire.com/store/mi/battle-creek/s/1591	1591
https://www.discounttire.com/store/mi/benton-harbor/s/1157	1157
https://www.discounttire.com/store/mi/chesterfield/s/1132	1132
https://www.discounttire.com/store/mi/grandville/s/1530	1530
https://www.discounttire.com/store/mi/holland/s/1575	1575
https://www.discounttire.com/store/mi/jackson/s/1126	1126
https://www.discounttire.com/store/mi/kalamazoo/s/1147	1147
https://www.discounttire.com/store/mi/kalamazoo/s/1148	1148
https://www.discounttire.com/store/mi/kalamazoo/s/1592	1592
https://www.discounttire.com/store/mi/lansing/s/1152	1152
https://www.discounttire.com/store/mi/lathrup-village/s/1644	1644
https://www.discounttire.com/store/mi/midland/s/1155	1155
https://www.discounttire.com/store/mn/eden-prairie/s/1495	1495
https://www.discounttire.com/store/mn/saint-paul/s/1538	1538
https://www.discounttire.com/store/mn/west-st-paul/s/1796	1796
https://www.discounttire.com/store/nm/alamogordo/s/1908	1908
https://www.discounttire.com/store/nm/farmington/s/1650	1650
https://www.discounttire.com/store/oh/avon/s/1979	1979
https://www.discounttire.com/store/oh/beavercreek/s/1996	1996
https://www.discounttire.com/store/oh/cincinnati/s/2071	2071
https://www.discounttire.com/store/oh/lancaster/s/1666	1666
https://www.discounttire.com/store/oh/rossford/s/1770	1770
https://www.discounttire.com/store/oh/west-chester/s/2036	2036
https://www.discounttire.com/store/wa/bothell/s/1589	1589
https://www.discounttire.com/store/wa/bremerton/s/1275	1275
https://www.discounttire.com/store/wa/everett/s/1265	1265
https://www.discounttire.com/store/wa/pasco/s/1818	1818
https://www.discounttire.com/store/wa/renton/s/1268	1268
https://www.discounttire.com/store/wa/tacoma/s/1267	1267
https://www.discounttire.com/store/wa/vancouver/s/1278	1278
https://www.discounttire.com/store/wi/madison/s/1716	1716
https://www.discounttire.com/store/co/boulder/s/1088	1088
https://www.discounttire.com/store/co/parker/s/1665	1665
https://www.discounttire.com/store/il/aurora/s/1535	1535
https://www.discounttire.com/store/il/bloomingdale/s/1316	1316
https://www.discounttire.com/store/il/countryside/s/1315	1315
https://www.discounttire.com/store/il/mount-prospect/s/1508	1508
https://www.discounttire.com/store/il/oswego/s/1388	1388
https://www.discounttire.com/store/la/baton-rouge/s/2223	2223
https://www.discounttire.com/store/tx/azle/s/2306	2306
https://www.discounttire.com/store/tx/magnolia/s/2262	2262
https://www.discounttire.com/store/az/prescott-valley/s/2261	2261
https://www.discounttire.com/store/nc/matthews/s/2247	2247
https://www.discounttire.com/store/tx/lubbock/s/2277	2277
https://www.discounttire.com/store/ga/rome/s/2258	2258
https://www.discounttire.com/store/mo/saint-peters/s/2263	2263
https://www.discounttire.com/store/mo/st.-louis/s/2231	2231
https://www.discounttire.com/store/ga/flowery-branch/s/2274	2274
https://www.discounttire.com/store/mo/hazelwood/s/2286	2286
https://www.discounttire.com/store/mo/saint-ann/s/2275	2275
https://www.discounttire.com/store/va/cave-spring/s/2279	2279
https://www.discounttire.com/store/va/virginia-beach/s/2257	2257
https://www.discounttire.com/store/ar/russellville/s/2347	2347
https://www.discounttire.com/store/fl/jacksonville/s/2376	2376
https://www.discounttire.com/store/ar/mountain-home/s/2338	2338
https://www.discounttire.com/store/nc/goldsboro/s/2283	2283
https://www.discounttire.com/store/nc/greensboro/s/2301	2301
https://www.discounttire.com/store/nc/sanford/s/2354	2354
https://www.discounttire.com/store/tx/pasadena/s/2329	2329
https://www.discounttire.com/store/tx/san-antonio/s/2291	2291
https://www.discounttire.com/store/mi/monroe/s/2302	2302
https://www.discounttire.com/store/mn/cottage-grove/s/2426	2426
https://www.discounttire.com/store/ut/st.-george/s/2352	2352
https://www.discounttire.com/store/wi/brookfield/s/2432	2432
https://www.discounttire.com/store/mo/lake-st-louis/s/2337	2337
https://www.discounttire.com/store/mo/rolla/s/2323	2323
https://www.discounttire.com/store/nd/grand-forks/s/2280	2280
https://www.discounttire.com/store/pa/west-mifflin/s/2295	2295
https://www.discounttire.com/store/mi/grand-blanc/s/2326	2326
https://www.discounttire.com/store/mo/saint-peters/s/2315	2315
https://www.discounttire.com/store/wi/kenosha/s/2361	2361
https://www.discounttire.com/store/al/madison/s/2097	2097
https://www.discounttire.com/store/ca/chula-vista/s/2203	2203
https://www.discounttire.com/store/ca/national-city/s/1070	1070
https://www.discounttire.com/store/ca/oceanside/s/1374	1374
https://www.discounttire.com/store/ca/san-diego/s/1066	1066
https://www.discounttire.com/store/ca/san-diego/s/1076	1076
https://www.discounttire.com/store/ca/san-diego/s/1711	1711
https://www.discounttire.com/store/ca/san-marcos/s/1521	1521
https://www.discounttire.com/store/ca/vista/s/1904	1904
https://www.discounttire.com/store/fl/clermont/s/1689	1689
https://www.discounttire.com/store/fl/gainesville/s/1715	1715
https://www.discounttire.com/store/fl/jacksonville/s/1730	1730
https://www.discounttire.com/store/fl/ocala/s/1670	1670
https://www.discounttire.com/store/fl/orlando/s/1117	1117
https://www.discounttire.com/store/fl/palm-coast/s/2164	2164
https://www.discounttire.com/store/fl/rockledge/s/1894	1894
https://www.discounttire.com/store/fl/west-melbourne/s/1843	1843
https://www.discounttire.com/store/fl/winter-haven/s/1781	1781
https://www.discounttire.com/store/ga/acworth/s/1654	1654
https://www.discounttire.com/store/ga/alpharetta/s/2119	2119
https://www.discounttire.com/store/ga/augusta/s/1931	1931
https://www.discounttire.com/store/ga/austell/s/1519	1519
https://www.discounttire.com/store/ga/conyers/s/1911	1911
https://www.discounttire.com/store/ga/gainesville/s/1655	1655
https://www.discounttire.com/store/ga/hiram/s/1703	1703
https://www.discounttire.com/store/ga/lawrenceville/s/1551	1551
https://www.discounttire.com/store/ga/lilburn/s/1658	1658
https://www.discounttire.com/store/ga/marietta/s/2136	2136
https://www.discounttire.com/store/ga/mcdonough/s/1690	1690
https://www.discounttire.com/store/ga/warner-robins/s/1786	1786
https://www.discounttire.com/store/ga/woodstock/s/1483	1483
https://www.discounttire.com/store/ks/derby/s/2005	2005
https://www.discounttire.com/store/ks/wichita/s/2111	2111
https://www.discounttire.com/store/ky/louisville/s/1927	1927
https://www.discounttire.com/store/ky/louisville/s/2024	2024
https://www.discounttire.com/store/la/bossier-city/s/2179	2179
https://www.discounttire.com/store/ms/southaven/s/2003	2003
https://www.discounttire.com/store/mt/helena/s/2099	2099
https://www.discounttire.com/store/mt/kalispell/s/2027	2027
https://www.discounttire.com/store/nc/arden/s/1854	1854
https://www.discounttire.com/store/nc/charlotte/s/1969	1969
https://www.discounttire.com/store/nc/mooresville/s/1621	1621
https://www.discounttire.com/store/nc/raleigh/s/1486	1486
https://www.discounttire.com/store/nc/raleigh/s/1741	1741
https://www.discounttire.com/store/nc/raleigh/s/1914	1914
https://www.discounttire.com/store/nc/salisbury/s/1819	1819
https://www.discounttire.com/store/nv/henderson/s/1766	1766
https://www.discounttire.com/store/nv/las-vegas/s/1463	1463
https://www.discounttire.com/store/nv/las-vegas/s/1842	1842
https://www.discounttire.com/store/ok/ardmore/s/2253	2253
https://www.discounttire.com/store/ok/del-city/s/1907	1907
https://www.discounttire.com/store/ok/lawton/s/1985	1985
https://www.discounttire.com/store/ok/oklahoma-city/s/1777	1777
https://www.discounttire.com/store/ok/oklahoma-city/s/1807	1807
https://www.discounttire.com/store/ok/yukon/s/1856	1856
https://www.discounttire.com/store/sc/greenville/s/1503	1503
https://www.discounttire.com/store/sc/n-charleston/s/2233	2233
https://www.discounttire.com/store/tn/bartlett/s/2077	2077
https://www.discounttire.com/store/tn/collierville/s/2095	2095
https://www.discounttire.com/store/tn/gallatin/s/1804	1804
https://www.discounttire.com/store/tn/hixson/s/2090	2090
https://www.discounttire.com/store/tn/knoxville/s/2227	2227
https://www.discounttire.com/store/tn/madison/s/1754	1754
https://www.discounttire.com/store/tn/memphis/s/2064	2064
https://www.discounttire.com/store/va/chester/s/2229	2229
https://www.discounttire.com/store/va/chesterfield/s/2109	2109
https://www.discounttire.com/store/va/fredericksburg/s/2230	2230
https://www.discounttire.com/store/va/waynesboro/s/2185	2185
https://www.discounttire.com/store/az/buckeye/s/1861	1861
https://www.discounttire.com/store/az/casa-grande/s/1661	1661
https://www.discounttire.com/store/az/gilbert/s/1679	1679
https://www.discounttire.com/store/az/goodyear/s/1555	1555
https://www.discounttire.com/store/az/lake-havasu-city/s/1561	1561
https://www.discounttire.com/store/az/laveen/s/1918	1918
https://www.discounttire.com/store/az/mesa/s/1027	1027
https://www.discounttire.com/store/az/mesa/s/1426	1426
https://www.discounttire.com/store/az/mesa/s/1688	1688
https://www.discounttire.com/store/az/phoenix/s/1018	1018
https://www.discounttire.com/store/az/san-tan-valley/s/2187	2187
https://www.discounttire.com/store/az/scottsdale/s/1874	1874
https://www.discounttire.com/store/az/sierra-vista/s/1029	1029
https://www.discounttire.com/store/az/tempe/s/1026	1026
https://www.discounttire.com/store/az/tucson/s/1031	1031
https://www.discounttire.com/store/nc/charlotte/s/1487	1487
https://www.discounttire.com/store/nm/las-cruces/s/1164	1164
https://www.discounttire.com/store/nm/roswell/s/1728	1728
https://www.discounttire.com/store/tn/franklin/s/1753	1753
https://www.discounttire.com/store/tn/nashville/s/1881	1881
https://www.discounttire.com/store/tx/amarillo/s/1761	1761
https://www.discounttire.com/store/tx/arlington/s/1206	1206
https://www.discounttire.com/store/tx/austin/s/1177	1177
https://www.discounttire.com/store/tx/austin/s/1279	1279
https://www.discounttire.com/store/tx/austin/s/2222	2222
https://www.discounttire.com/store/tx/balch-springs/s/2078	2078
https://www.discounttire.com/store/tx/baytown/s/1221	1221
https://www.discounttire.com/store/tx/beaumont/s/1529	1529
https://www.discounttire.com/store/tx/canutillo/s/1839	1839
https://www.discounttire.com/store/tx/clear-lake-shores/s/1598	1598
https://www.discounttire.com/store/tx/corpus-christi/s/1509	1509
https://www.discounttire.com/store/tx/corpus-christi/s/1866	1866
https://www.discounttire.com/store/tx/dallas/s/1280	1280
https://www.discounttire.com/store/tx/decatur/s/2079	2079
https://www.discounttire.com/store/tx/denton/s/2161	2161
https://www.discounttire.com/store/tx/denton/s/2202	2202
https://www.discounttire.com/store/tx/desoto/s/1491	1491
https://www.discounttire.com/store/tx/early/s/2028	2028
https://www.discounttire.com/store/tx/el-paso/s/1208	1208
https://www.discounttire.com/store/tx/el-paso/s/1995	1995
https://www.discounttire.com/store/tx/forest-hill/s/1445	1445
https://www.discounttire.com/store/tx/granbury/s/1695	1695
https://www.discounttire.com/store/tx/grand-prairie/s/1185	1185
https://www.discounttire.com/store/tx/gun-barrel-city/s/2235	2235
https://www.discounttire.com/store/tx/harlingen/s/1181	1181
https://www.discounttire.com/store/tx/hill-country-village/s/1253	1253
https://www.discounttire.com/store/tx/houston/s/1211	1211
https://www.discounttire.com/store/tx/houston/s/1224	1224
https://www.discounttire.com/store/tx/houston/s/1227	1227
https://www.discounttire.com/store/tx/houston/s/1237	1237
https://www.discounttire.com/store/tx/houston/s/1241	1241
https://www.discounttire.com/store/tx/houston/s/1438	1438
https://www.discounttire.com/store/tx/houston/s/1719	1719
https://www.discounttire.com/store/tx/houston/s/2163	2163
https://www.discounttire.com/store/tx/katy/s/1296	1296
https://www.discounttire.com/store/tx/katy/s/1977	1977
https://www.discounttire.com/store/tx/killeen/s/1490	1490
https://www.discounttire.com/store/tx/laredo/s/1714	1714
https://www.discounttire.com/store/tx/laredo/s/1942	1942
https://www.discounttire.com/store/tx/leander/s/1972	1972
https://www.discounttire.com/store/tx/lewisville/s/1290	1290
https://www.discounttire.com/store/tx/longview/s/1451	1451
https://www.discounttire.com/store/tx/lubbock/s/1245	1245
https://www.discounttire.com/store/tx/meadows-place/s/1222	1222
https://www.discounttire.com/store/tx/midland/s/1246	1246
https://www.discounttire.com/store/tx/midlothian/s/2204	2204
https://www.discounttire.com/store/tx/pasadena/s/1380	1380
https://www.discounttire.com/store/tx/pflugerville/s/1859	1859
https://www.discounttire.com/store/tx/plano/s/1205	1205
https://www.discounttire.com/store/tx/san-angelo/s/1939	1939
https://www.discounttire.com/store/tx/san-antonio/s/1249	1249
https://www.discounttire.com/store/tx/san-antonio/s/1543	1543
https://www.discounttire.com/store/tx/san-antonio/s/1945	1945
https://www.discounttire.com/store/tx/san-antonio/s/2018	2018
https://www.discounttire.com/store/tx/san-antonio/s/2083	2083
https://www.discounttire.com/store/tx/schertz/s/2198	2198
https://www.discounttire.com/store/tx/spring/s/1320	1320
https://www.discounttire.com/store/tx/victoria/s/1528	1528
https://www.discounttire.com/store/tx/wichita-falls/s/1247	1247
https://www.discounttire.com/store/va/norfolk/s/2209	2209
https://www.discounttire.com/store/wa/yakima/s/2148	2148
https://www.discounttire.com/store/az/gilbert/s/1686	1686
https://www.discounttire.com/store/az/tucson/s/1455	1455
https://www.discounttire.com/store/ia/altoona/s/2037	2037
https://www.discounttire.com/store/ia/cedar-rapids/s/1984	1984
https://www.discounttire.com/store/ia/des-moines/s/2063	2063
https://www.discounttire.com/store/ia/dubuque/s/2030	2030
https://www.discounttire.com/store/id/ammon/s/2039	2039
https://www.discounttire.com/store/id/boise/s/2009	2009
https://www.discounttire.com/store/il/johnsburg/s/2182	2182
https://www.discounttire.com/store/ks/olathe/s/2145	2145
https://www.discounttire.com/store/ks/shawnee/s/2059	2059
https://www.discounttire.com/store/mi/ann-arbor/s/1123	1123
https://www.discounttire.com/store/ne/omaha/s/1955	1955
https://www.discounttire.com/store/nv/reno/s/1792	1792
https://www.discounttire.com/store/or/bend/s/1693	1693
https://www.discounttire.com/store/or/gresham/s/1175	1175
https://www.discounttire.com/store/or/tigard/s/1173	1173
https://www.discounttire.com/store/pa/pittsburgh/s/2186	2186
https://www.discounttire.com/store/tx/bedford/s/1194	1194
https://www.discounttire.com/store/tx/houston/s/1234	1234
https://www.discounttire.com/store/tx/houston/s/1332	1332
https://www.discounttire.com/store/tx/houston/s/1334	1334
https://www.discounttire.com/store/tx/humble/s/1764	1764
https://www.discounttire.com/store/tx/hurst/s/1182	1182
https://www.discounttire.com/store/tx/pearland/s/1603	1603
https://www.discounttire.com/store/tx/porter/s/2142	2142
https://www.discounttire.com/store/tx/prosper/s/1800	1800
https://www.discounttire.com/store/tx/spring/s/1448	1448
https://www.discounttire.com/store/tx/tomball/s/1552	1552
https://www.discounttire.com/store/ut/bountiful/s/1462	1462
https://www.discounttire.com/store/ut/draper/s/1697	1697
https://www.discounttire.com/store/ut/lindon/s/1613	1613
https://www.discounttire.com/store/ut/orem/s/1257	1257
https://www.discounttire.com/store/ut/washington/s/1570	1570
https://www.discounttire.com/store/ut/west-jordan/s/2160	2160
https://www.discounttire.com/store/va/henrico/s/2102	2102
https://www.discounttire.com/store/va/north-chesterfield/s/2045	2045
https://www.discounttire.com/store/va/suffolk/s/2057	2057
https://www.discounttire.com/store/co/aurora/s/1735	1735
https://www.discounttire.com/store/co/colorado-springs/s/1513	1513
https://www.discounttire.com/store/co/englewood/s/1105	1105
https://www.discounttire.com/store/co/lakewood/s/1093	1093
https://www.discounttire.com/store/co/lone-tree/s/1501	1501
https://www.discounttire.com/store/co/westminster/s/1308	1308
https://www.discounttire.com/store/il/glendale-heights/s/1461	1461
https://www.discounttire.com/store/il/joliet/s/1321	1321
https://www.discounttire.com/store/il/matteson/s/1636	1636
https://www.discounttire.com/store/il/new-lenox/s/1891	1891
https://www.discounttire.com/store/il/normal/s/1824	1824
https://www.discounttire.com/store/il/orland-park/s/1660	1660
https://www.discounttire.com/store/il/st-charles/s/1971	1971
https://www.discounttire.com/store/in/avon/s/1888	1888
https://www.discounttire.com/store/in/carmel/s/1415	1415
https://www.discounttire.com/store/in/kokomo/s/1493	1493
https://www.discounttire.com/store/in/michigan-city/s/2134	2134
https://www.discounttire.com/store/in/mishawaka/s/1122	1122
https://www.discounttire.com/store/in/portage/s/1877	1877
https://www.discounttire.com/store/mi/auburn-hills/s/1525	1525
https://www.discounttire.com/store/mi/burton/s/1139	1139
https://www.discounttire.com/store/mi/clinton-township/s/1131	1131
https://www.discounttire.com/store/mi/comstock-park/s/1351	1351
https://www.discounttire.com/store/mi/grand-rapids/s/2113	2113
https://www.discounttire.com/store/mi/lansing/s/1531	1531
https://www.discounttire.com/store/mi/novi/s/1127	1127
https://www.discounttire.com/store/mi/okemos/s/1151	1151
https://www.discounttire.com/store/mi/sterling-heights/s/1595	1595
https://www.discounttire.com/store/mi/woodhaven/s/1468	1468
https://www.discounttire.com/store/mi/ypsilanti/s/1579	1579
https://www.discounttire.com/store/mn/apple-valley/s/1798	1798
https://www.discounttire.com/store/mn/blaine/s/1604	1604
https://www.discounttire.com/store/mn/bloomington/s/1571	1571
https://www.discounttire.com/store/mn/lino-lakes/s/1576	1576
https://www.discounttire.com/store/mn/minnetonka/s/1586	1586
https://www.discounttire.com/store/mn/stillwater/s/1622	1622
https://www.discounttire.com/store/mn/waite-park/s/1832	1832
https://www.discounttire.com/store/nm/albuquerque/s/1163	1163
https://www.discounttire.com/store/oh/columbus/s/2029	2029
https://www.discounttire.com/store/oh/macedonia/s/1951	1951
https://www.discounttire.com/store/oh/miamisburg/s/1500	1500
https://www.discounttire.com/store/oh/toledo/s/1606	1606
https://www.discounttire.com/store/wa/bellevue/s/1266	1266
https://www.discounttire.com/store/wa/lynnwood/s/1277	1277
https://www.discounttire.com/store/wa/renton/s/1745	1745
https://www.discounttire.com/store/wa/richland/s/1850	1850
https://www.discounttire.com/store/wa/seattle/s/1270	1270
https://www.discounttire.com/store/wa/shoreline/s/1698	1698
https://www.discounttire.com/store/wa/wenatchee/s/1778	1778
https://www.discounttire.com/store/wi/appleton/s/2016	2016
https://www.discounttire.com/store/al/prattville/s/2282	2282
https://www.discounttire.com/store/co/colorado-springs/s/1111	1111
https://www.discounttire.com/store/co/colorado-springs/s/1610	1610
https://www.discounttire.com/store/co/fort-collins/s/1625	1625
https://www.discounttire.com/store/co/greeley/s/1794	1794
https://www.discounttire.com/store/ga/pooler/s/2276	2276
https://www.discounttire.com/store/il/lombard/s/1289	1289
https://www.discounttire.com/store/nm/rio-rancho/s/2372	2372
https://www.discounttire.com/store/wi/wausau/s/2200	2200
https://www.discounttire.com/store/ga/columbus/s/2305	2305
https://www.discounttire.com/store/wi/madison/s/2265	2265
https://www.discounttire.com/store/oh/medina/s/2255	2255
https://www.discounttire.com/store/ky/elizabethtown/s/2267	2267
https://www.discounttire.com/store/nm/santa-fe/s/2197	2197
https://www.discounttire.com/store/fl/orlando/s/2385	2385
https://www.discounttire.com/store/ca/oceanside/s/2250	2250
https://www.discounttire.com/store/fl/orlando/s/2389	2389
https://www.discounttire.com/store/nc/fayetteville/s/2370	2370
https://www.discounttire.com/store/nc/fayetteville/s/2396	2396
https://www.discounttire.com/store/tx/frisco/s/2365	2365
https://www.discounttire.com/store/tx/oak-hill/s/2345	2345
https://www.discounttire.com/store/ok/edmond/s/2333	2333
https://www.discounttire.com/store/tx/del-rio/s/2325	2325
https://www.discounttire.com/store/fl/davie/s/2290	2290
https://www.discounttire.com/store/il/glen-carbon/s/2343	2343
https://www.discounttire.com/store/co/peyton/s/2331	2331
https://www.discounttire.com/store/or/medford/s/2317	2317
https://www.discounttire.com/store/co/montrose/s/2312	2312
https://www.discounttire.com/store/il/gurnee/s/2349	2349
https://www.discounttire.com/store/ks/salina/s/2320	2320
https://www.discounttire.com/store/mo/arnold/s/2314	2314
https://www.discounttire.com/store/mo/festus/s/2359	2359
https://www.discounttire.com/store/ne/lincoln/s/2356	2356
https://www.discounttire.com/store/wi/la-crosse/s/2327	2327

    """.strip().split("\n")

    # Create the redirect map
    final_redirects = create_redirect_map(bad_urls, good_map_input)
    
    # --- Step 3: Write the results to a CSV file ---
    output_filename = 'redirects.csv'
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Define the column headers
        fieldnames = ['Bad URL', 'Good URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()
        
        # Write the data rows
        for bad, good in final_redirects.items():
            writer.writerow({'Bad URL': bad, 'Good URL': good})

    print(f"✅ Awesome! Your redirect map has been saved to '{output_filename}'")