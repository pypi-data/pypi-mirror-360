from nemo_library.adapter.hubspot.adapter import HubspotAdapter

if __name__ == "__main__":

    # Create an instance of the HubspotAdapter with default parameters
    adapter = HubspotAdapter()

    # Print the configuration to verify initialization
    print(adapter.config.hubspot_api_token)
    
    # You can add more functionality here, such as calling methods on the adapter
    # or performing operations related to HubSpot integration.