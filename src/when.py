import io
import reverse_geocoder
import pandas as pd

from datetime import datetime
from typing import List

from pathlib import Path
from exif2pandas import extract



class When:
    def __int__(
            self,
            feather_location,
            pictures_root: List[Path],
            cities_file=None,
            exclude_countries=(),
            processes=5,
    ):
        self.cities_file = cities_file
        self.exclude_countries = exclude_countries
        self.feather_location = feather_location

        # get raw dataframe with wide exif rows
        self.raw_exif_df = extract.extract_feather(
            feather_path=Path(feather_location).resolve(),
            pictures_root=pictures_root,
            processes=processes
        )

        # extract country name from gps data
        self.countries_df = self.get_countries_df()

        # create intervals based on the dates and gps
        self.intervals = self.get_intervals()
        self.intervals_df = pd.DataFrame(self.intervals)

        # create dataframe where every day has country code:
        self.day_df = self.get_country_per_day_df()


    def get_countries_df(self):
        """
        Returns dataframe with country and city name taken from gps data
        """
        with open(self.cities_file, encoding='utf-8') as f:
            self.geocoder = reverse_geocoder.RGeocoder(
                mode=2,
                verbose=True,
                stream=io.StringIO(f.read())
            )

        # for the location purposed we can drop all the other columns,
        # this is needed for .dropna
        df_location = (
            self.raw_exif_df[['cleaned_longitude', 'cleaned_latitude', 'cleaned_date']]
            .dropna()
            .set_index('cleaned_date')
        )

        tuple_locs = [
            (float(x), float(y))
            for x, y in
            df_location[
                ['cleaned_latitude', 'cleaned_longitude']
            ].itertuples(index=False)
        ]
        country_df = pd.DataFrame(self.geocoder.query(tuple_locs))
        # add date index, geocoder preservers the
        # order of the rows so this is fine
        country_df.index = df_location.index
        return df_location.join(country_df)


    def get_intervals(self):
        # lol the most hacky way to get the index at loc 0
        previous_date = datetime(1993, 11, 30)
        # previous_date = list(full_df[:1].to_dict(orient='index').keys())[0]
        previous_country_code = 'CZ'
        previous_country = 'Czech Republic'

        intervals = []

        for dt, row in self.countries_df.iterrows():
            country_code = row['cc']
            country = row['admin1']

            if country_code in self.exclude_countries:
                continue

            if country_code != previous_country_code:
                days = (dt - previous_date).days

                # if days == 0:
                #     continue

                intervals.append({
                    'from': previous_date.date(),
                    'to': dt.date().isoformat(),
                    'days': days,
                    'country': previous_country,
                    'country_code': previous_country_code
                })
                previous_date = dt
                previous_country_code = country_code
                previous_country = country


        # add the last interval
        dt = datetime.today()
        days = (dt - previous_date).days
        intervals.append({
            'from': previous_date.date(),
            'to': dt.date().isoformat(),
            'days': days,
            'country': previous_country,
            'country_code': previous_country_code
        })

        return intervals


    def get_country_per_day_df(self):
        intervals_full = []

        for i in self.intervals:
            for day in pd.date_range(i['from'], i['to']):
                intervals_full.append({
                    'day': day,
                    'country': i['country'],
                    'country_code': i['country_code']
                })

        df_days = pd.DataFrame(intervals_full).set_index('day').astype({
            'country': 'string',
            'country_code': 'string',
        })
        return df_days