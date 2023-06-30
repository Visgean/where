import io

import pandas as pd

from datetime import datetime
from typing import List, Optional

from pathlib import Path
from exif2pandas import extract
import pkg_resources


class Where:
    def __init__(
            self,
            pictures_root: List[Path],
            feather_location = None,
            cities_file=None,
            ignore_countries=(),
            processes=5,
            first_interval: Optional[datetime.date] = None,
            last_interval: Optional[datetime.date] = None,
    ):
        self.cities_file = cities_file
        if cities_file is None:
            self.cities_file = pkg_resources.resource_filename('photos_where', 'cities.csv')

        self.ignore_countries = ignore_countries
        self.feather_location = feather_location
        self.first_interval = first_interval
        self.last_interval = last_interval

        # get raw dataframe with wide exif rows
        self.raw_exif_df = extract.extract_feather(
            feather_path=Path(feather_location).resolve(),
            pictures_root=pictures_root,
            processes=processes
        )

        # extract country name from gps data
        self.countries_df = self._get_countries_df()

        # create intervals based on the dates and gps
        self.intervals = self._get_intervals()
        self.intervals_df = pd.DataFrame(self.intervals)

        # create dataframe where every day has country code:
        self.day_df = self._get_country_per_day_df()


    def _get_countries_df(self):
        """
        Returns dataframe with country and city name taken from gps data
        """
        import reverse_geocoder
        if self.cities_file:
            with open(self.cities_file, encoding='utf-8') as f:
                geocoder = reverse_geocoder.RGeocoder(
                    mode=2,
                    verbose=True,
                    stream=io.StringIO(f.read())
                )
        else:
            print('using geocoder default cities file')
            geocoder = reverse_geocoder.RGeocoder(
                mode=2,
                verbose=True,
                stream=None,
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
        country_df = pd.DataFrame(geocoder.query(tuple_locs))
        # add date index, geocoder preservers the
        # order of the rows so this is fine
        country_df.index = df_location.index
        return df_location.join(country_df)


    def _get_intervals(self):
        first_row = self.countries_df[:1].to_dict(orient='index')
        previous_date = list(first_row.keys())[0]
        previous_country_code = first_row[previous_date]['cc']
        previous_country = first_row[previous_date]['admin1']


        if self.first_interval:
            previous_date = self.first_interval

        intervals = []

        for dt, row in self.countries_df.iterrows():
            country_code = row['cc']
            country = row['admin1']

            if country_code in self.ignore_countries:
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
        if self.last_interval:
            last_interval = self.last_interval

        else:
            last_interval = datetime.today()

        days = (last_interval - previous_date).days
        intervals.append({
            'from': previous_date.date(),
            'to': last_interval.date().isoformat(),
            'days': days,
            'country': previous_country,
            'country_code': previous_country_code
        })

        return intervals


    def _get_country_per_day_df(self):
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