import requests
import json
import argparse


class URL:

    # RESOURCES = [ # "characters", "concepts", "episodes", "locations",  "objects", "origins", "people", "powers", # TODO again: "issues",   "movies",   
    #             # "promos", "publishers", "series_list", "search", "story_arcs", "teams", "types",
    #             # "videos", "video_types", "video_categories", "volumes"]

    RESOURCES = ["movies"]

    def __init__(self, url):
        self.url = url 

        self.generate_getters_and_setters()

    def generate_getters_and_setters(self):
        for resource in self.RESOURCES:
            setattr(self, f"get_{resource}_url", self.getter_generator_url(resource))
            setattr(self, f"get_{resource}", self.getter_generator(resource))


    def getter_generator_url(self, resource):  
        def internal_getter_url(**parameters):  
            default_parameters = { "api_key": "", "format": "", "field_list": "", "limit": "",                       
                                   "offset": "", "sort": "", "filter": "", "video_type": "", 
                                   "subscriber_only": "", "query": "", "resources": ""}
            return self.get_URL(resource, {**default_parameters, **parameters})

        internal_getter_url.__name__ = f"get_{resource}_url"
        
        return internal_getter_url

    def getter_generator(self, resource):  
        def internal_getter(session, **parameters):  
            default_parameters = { "api_key": "", "format": "", "field_list": "", "limit": "",                       
                                   "offset": "", "sort": "", "filter": "", "video_type": "", 
                                   "subscriber_only": "", "query": "", "resources": ""}
            return self.get_resource(session, resource, {**default_parameters, **parameters})

        internal_getter.__name__ = f"get_{resource}"
        
        return internal_getter

    def get_URL(self, resource, parameters):
        return f"{self.url}/{resource}/?api_key={parameters['api_key']}&"\
               f"format={parameters['format']}&"\
               f"field_list={parameters['field_list']}&"\
               f"limit={parameters['limit']}&"\
               f"offset={parameters['offset']}&"\
               f"sort={parameters['sort']}&"\
               f"filter={parameters['filter']}&"\
               f"video_type={parameters['video_type']}&"\
               f"subscriber_only={parameters['subscriber_only']}&"\
               f"query={parameters['query']}&"\
               f"resources={parameters['resources']}"

    def get_resource(self, session, resource, parameters):
        # adding headers, since website forbids web scrapping without user agent specified
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        get_resource_url = getattr(self, f"get_{resource}_url")
        print(f"\nURL: {get_resource_url(**parameters)}")
        return session.get(get_resource_url(**parameters), headers=headers) 


if __name__ == "__main__":
    
    url = URL("https://comicvine.gamespot.com/api")
    format = "json"

    # python url.py -api-key 1232hgwer3742f8 -res all
    # python url.py -api-key 1232hgwer3742f8 -res videos
    # python url.py -api-key 1232hgwer3742f8 -res videos types
    parser = argparse.ArgumentParser(description="Input everything you need to extract the data")
    parser.add_argument("-api-key", "--api-key", help="API key value", required=True)
    parser.add_argument("-res", "--resource", choices=["all"] + url.RESOURCES, help="Specify resource to download", required=True, default="all", nargs="+", type=str)

    args = parser.parse_args()

    resources = url.RESOURCES if args.resource == ["all"] else args.resource
    print(resources)

    for resource in url.RESOURCES:

        with requests.Session() as s:
            collected_data = []

            # first request
            get_resource = getattr(url, f"get_{resource}")
            offset = 0
            try:
                r = get_resource(s, api_key=args.api_key, format=format, offset=offset).json()
                total_number_results = int(r["number_of_total_results"])

                error = r["error"]
                step = int(r["number_of_page_results"])
                offset = int(r["offset"])
                
                if error == "OK":
                    collected_data.extend(r["results"])

                print(f"---> {offset}/{total_number_results} | error: {error} | step: {step}")
                
                offset += step

            except:
                print(f"Couldn't parse JSON with offset = 0... Try with smaller steps")
                offset_old = offset
                step = 100
                step_sm = 1
                while offset_old <= offset < offset_old + step:
                    try:
                        r = get_resource(s, api_key=args.api_key, format=format, offset=offset, limit=step_sm).json()
                        error = r["error"]
                        step_sm = int(r["number_of_page_results"])
                        offset = int(r["offset"])
                        
                        if error == "OK":
                            collected_data.extend(r["results"])
                        
                        print(f"---> {offset}/{total_number_results} | error: {error}/OK | step: {step_sm}/1")
 
                    except:
                        print(f"Couldn't parse JSON with offset = {offset}...")
                        
                    offset += 1
            
            # other requests
            offset_old = offset
            while offset_old <= offset < total_number_results - step:
                
                try:
                    r = get_resource(s, api_key=args.api_key, format=format, offset=offset).json()

                    error = r["error"]
                    step = r["number_of_page_results"]
                    offset = r["offset"]

                    if error == "OK":
                        collected_data.extend(r["results"])

                    print(f"---> {offset}/{total_number_results} | error: {error}/OK | step: {step}")
                
                    offset += step
                
                except:
                    print(f"Couldn't parse JSON with offset = {offset}... Try with smaller steps")
                    offset_old = offset
                    step_sm = 1
                    while offset_old <= offset < offset_old + step:
                        try:
                            r = get_resource(s, api_key=args.api_key, format=format, offset=offset, limit=step_sm).json()
                            error = r["error"]
                            step_sm = int(r["number_of_page_results"])
                            offset = int(r["offset"])
                            
                            if error == "OK":
                                collected_data.extend(r["results"])
                            
                            print(f"---> {offset}/{total_number_results} | error: {error}/OK | step: {step_sm}/1")
    
                        except:
                            print(f"Couldn't parse JSON with offset = {offset}...")
                            
                        offset += 1

        print(f"Lenth of the list {len(collected_data)}")
        directory_statements = "../ComicVine"
        with open(f"{directory_statements}/{resource}.json", "w") as f:
            json.dump(collected_data, f)
        