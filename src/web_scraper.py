import requests
from bs4 import BeautifulSoup
import pandas as pd
import collections

collections.Callable = collections.abc.Callable


def scores_and_ranks(url):
    '''
    For each table, iterate over all rows to find the content scores and ranks for each group.
    '''
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")[1::2]
    table_dfs = []

    for table_num, table in enumerate(tables):
        rows_data = []
        
        rows = table.find_all("tr")
        
        for row in rows:
            cols = row.find_all("td", recursive=False)
            
            if len(cols) < 3:
                continue
                
            row_dict = {
                "group": cols[0].get_text(strip=True),              ## first column has the group name -- trim whitespace
                "location": cols[1].get_text(strip=True)            ## second column has the group location -- trim whitespace
                }

            score_num = 1

            for td in cols[2:]:                                     ## third column and beyond have the scores and ranks
                score_td = td.select_one(".content.score")          ## returns a single element matching the "content score" class
                rank_td = td.select_one(".content.rank")            ## returns a single element matching the "content rank" class

                if score_td:                                        ## if a score exists, assign a score as dtype float and rank as dtype int to the respective dictionary row
                    score = score_td.get(
                        "data-translate-number",
                        score_td.get_text(strip=True)
                        )

                    rank = (
                        rank_td.get_text(strip=True)
                        if rank_td else None
                        )

                    row_dict[f"score_{score_num}"] = float(score)

                    row_dict[f"rank_{score_num}"] = (
                        int(rank) if rank and rank.isdigit() else None
                        )

                    score_num += 1

            rows_data.append(row_dict)

        if rows_data:
            df = pd.DataFrame(rows_data)
            table_dfs.append(df)

    return table_dfs
    ## Returns all tables on the webpage. 