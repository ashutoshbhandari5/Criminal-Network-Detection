import pandas as pd
import os


class FlitterDataLoader:
    def __init__(self, dataset_path="dataset/M2-Social Net and Geo"):
        self.dataset_path = dataset_path
        self.links_df = None
        self.entities_df = None
        self.locations_df = None
        self.flitter_names_df = None

    def load_all_data(self):
        print("Loading Flitter social network data..")

        self.links_df = self._load_links()
        print(f" Loaded {len(self.links_df)} social network connections")

        self.entities_df = self._load_entities()
        print(f" Loaded {len(self.entities_df)} entities")

        self.locations_df = self._load_locations()
        print(f" Loaded location data for {len(self.locations_df)} people")

        self.flitter_names_df = self._load_flitter_names()
        print(f" Loaded {len(self.flitter_names_df)} Flitter usernames")

        print("Done with data loading!\n")

        return {
            'links': self.links_df,
            'entities': self.entities_df,
            'locations': self.locations_df,
            'flitter_names': self.flitter_names_df
        }

    def _load_links(self):
        file_path = os.path.join(self.dataset_path, "Links_Table.txt")
        df = pd.read_csv(file_path, sep='\t', skiprows=2, names=['ID1', 'ID2'])
        df['ID1'] = df['ID1'].astype(int)
        df['ID2'] = df['ID2'].astype(int)
        return df

    def _load_entities(self):
        file_path = os.path.join(self.dataset_path, "Entities_Table.txt")
        df = pd.read_csv(file_path, sep='\t', skiprows=2, names=['ID', 'Name', 'Type'])
        df['ID'] = df['ID'].astype(int)
        return df

    def _load_locations(self):
        file_path = os.path.join(self.dataset_path, "People-Cities.txt")
        df = pd.read_csv(file_path, sep='\t', skiprows=2, names=['ID', 'City'])
        df['ID'] = df['ID'].astype(int)
        df['City'] = df['City'].str.strip()
        return df

    def _load_flitter_names(self):
        file_path = os.path.join(self.dataset_path, "Flitter Names.txt")
        df = pd.read_csv(file_path, sep='\t', header=None, names=['ID', 'FlitterName'])
        df['ID'] = df['ID'].astype(int)
        return df

    def get_person_info(self, person_id):
        info = {}

        entity_row = self.entities_df[self.entities_df['ID'] == person_id]
        if not entity_row.empty:
            info['name'] = entity_row.iloc[0]['Name']
            info['type'] = entity_row.iloc[0]['Type']

        location_row = self.locations_df[self.locations_df['ID'] == person_id]
        if not location_row.empty:
            info['city'] = location_row.iloc[0]['City']

        return info

    def get_all_cities(self):
        return sorted(self.locations_df['City'].unique().tolist())

    def get_people_by_city(self, city):
        return self.locations_df[self.locations_df['City'] == city]['ID'].tolist()

    def get_data_summary(self):
        return {
            'total_people': len(self.entities_df),
            'total_connections': len(self.links_df),
            'total_cities': len(self.get_all_cities()),
            'cities': self.get_all_cities()
        }


if __name__ == "__main__":
    loader = FlitterDataLoader()
    data = loader.load_all_data()

    summary = loader.get_data_summary()
    print("\nHere is the summary of dataset:")
    print(f"  Total People: {summary['total_people']}")
    print(f"  Total Connections: {summary['total_connections']}")
    print(f"  Total Cities: {summary['total_cities']}")
    print(f"  Cities: {', '.join(summary['cities'])}")
