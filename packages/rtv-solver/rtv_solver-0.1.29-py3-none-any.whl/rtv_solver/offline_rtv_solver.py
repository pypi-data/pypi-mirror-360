from .online_rtv_solver import OnlineRTVSolver
from .handlers.request_handler import RequestHandler
from .handlers.network_handler import NetworkHandler
from .handlers.vehicle_handler import VehicleHandler
from .handlers.trip_handler import TripHandler
from .handlers.payload_parser import PayloadParser
import copy

class OfflineRTVSolver:

    def __init__(self,server_url,SHAREABLE_COST_FACTOR=2,RTV_TIMEOUT=3000, LARGEST_TSP = 10, MAX_CARDINALITY = 8):
        self.ILP_SOLVER_TIMEOUT = 120 # seconds
        self.RTV_TIMEOUT = RTV_TIMEOUT #seconds
        self.PENALTY = 1000000 # penalty for not serving a trip
        self.SHAREABLE_COST_FACTOR = SHAREABLE_COST_FACTOR
        self.MAX_CARDINALITY = MAX_CARDINALITY
        self.MAX_THREAD_CNT = 64
        self.REBALANCING = False
        self.RH_FACTOR = 1
        self.DWELL_PICKUP = 180
        self.DWELL_ALIGHT = 60
        self.LARGEST_TSP = LARGEST_TSP
        self.server_url = server_url

    def solve_rtv(self, payload, interval, step_size, step_size_time = True):
        online_rtv_solver = OnlineRTVSolver(self.server_url,
            SHAREABLE_COST_FACTOR=self.SHAREABLE_COST_FACTOR,
            RTV_TIMEOUT=self.RTV_TIMEOUT, 
            LARGEST_TSP = self.LARGEST_TSP, 
            MAX_CARDINALITY = self.MAX_CARDINALITY,)

        # get the start_time
        start_time = 24*3600
        end_time = 0

        for request in payload["requests"]:
            if request["pickup_time_window_start"] < start_time:
                start_time = request["pickup_time_window_start"]
            if request["dropoff_time_window_end"] > end_time:
                end_time = request["dropoff_time_window_end"]

        current_time = max(0,start_time - interval)
        driver_runs = payload["driver_runs"]

        unserved_requests = []

        window_start_times = []
        for i in range(len(payload["requests"])):
            window_start_times.append((i,payload["requests"][i]["pickup_time_window_start"]))

        window_start_times.sort(key=lambda x: x[1])
        index = 0

        while current_time < end_time:
            # select the requests that are to be considered in the current interval
            selected_requests = {}
            if step_size_time:
                for request in payload["requests"]:
                    if request["pickup_time_window_start"] < current_time + interval and request["pickup_time_window_start"] >= current_time:
                        selected_requests[request["booking_id"]] = request
            else:
                for j in range(step_size):
                    if index < len(window_start_times):
                        request_index = window_start_times[index][0]
                        request = payload["requests"][request_index]
                        selected_requests[request["booking_id"]] = request
                        current_time = window_start_times[index][1]
                        index += 1
                    else:
                        current_time = end_time
            for dr in driver_runs:
                for stop in dr["manifest"]:
                    if stop["booking_id"] in selected_requests:
                        del selected_requests[stop["booking_id"]]
            
            selected_requests = list(selected_requests.values())


            # create a new payload with the selected requests
            new_payload = {
                "depot": payload["depot"],
                "requests": selected_requests,
                "driver_runs": driver_runs}

            # solve the RTV problem
            if len(selected_requests) == 0:
                new_driver_runs = driver_runs
            else:             
                new_driver_runs, unserved = online_rtv_solver.solve_pdptw_rtv(new_payload)
                unserved_requests.extend(unserved)
            if step_size_time:
                current_time += step_size

            # simulate the driver runs
            simulated_driver_runs = online_rtv_solver.simulate_manifest(current_time,new_driver_runs,intermediate_location=False)
            driver_runs = simulated_driver_runs

        return driver_runs, unserved_requests
