#!/usr/bin/env python3
import argparse
import os

from pathlib import Path
import matplotlib.pyplot as plt

from matplotlib.pyplot import savefig

from . import Where

parser = argparse.ArgumentParser(description="Generate analysis from your photos")
parser.add_argument("picture_folders", nargs="+", help="list of folders with the images")

parser.add_argument(
    "-f",
    "--feather",
    default='where/photos.feather',
    help="Output the data frame to feather file (this will override existing file!)",
)

parser.add_argument(
    '-o',
    '--output'
    "out", help="Output folder for the csv etc", default='where',
    dest='out'
)

parser.add_argument(
    '-i'
    "--ignore_countries",
    nargs="+",
    help="Country codes to ignore",
    dest='ignore'

)

parser.add_argument(
    "-p",
    "--processes",
    type=int,
    help="number of processes to use for collecting exif data, defaults to 5",
    default=5,
)


def main():
    args = parser.parse_args()

    out_dir = Path(args.out)
    os.makedirs(out_dir, exist_ok=True)
    picture_dirs = [Path(f).resolve() for f in args.picture_folders]

    feather_loc = None
    if args.feather:
        feather_loc = Path(args.feather).resolve()

    ignore_countries = []
    if args.ignore:
        ignore_countries = args.ignore

    where = Where(
        feather_location=feather_loc,
        pictures_root=picture_dirs,
        processes=5,
        ignore_countries=ignore_countries
    )

    where.day_df.to_csv(out_dir / 'location-by-day.csv')
    where.intervals_df.to_csv(out_dir / 'intervals.csv')

    where.countries_df.cc.value_counts().plot(kind='pie')
    savefig(out_dir / 'countries-pie.jpg')

    where.countries_df.admin2.value_counts().plot(kind='pie')
    savefig(out_dir / 'cities-pie.jpg')

    plt.style.use('seaborn-deep')
    fig = plt.figure(figsize=(15, 20))
    ax = fig.gca()

    where.day_df['country_code'].hist(by=where.day_df.index.year, ax=ax, rwidth=0.5)
    savefig(out_dir / 'years.jpg')


if __name__ == "__main__":
    main()
