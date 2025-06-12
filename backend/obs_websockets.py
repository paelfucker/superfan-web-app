import time
import sys
from obswebsocket import obsws, requests  # noqa: E402
from websockets_auth import WEBSOCKET_HOST, WEBSOCKET_PORT, WEBSOCKET_PASSWORD

class OBSWebsocketsManager:
    ws = None

    def __init__(self):
        self.ws = obsws(WEBSOCKET_HOST, WEBSOCKET_PORT, WEBSOCKET_PASSWORD)
        try:
            self.ws.connect()
        except:
            print("\nPANIC!!\nCOULD NOT CONNECT TO OBS!\nDouble check that you have OBS open and that your websockets server is enabled in OBS.")
            time.sleep(10)
            sys.exit()
        print("Connected to OBS Websockets!\n")

    def disconnect(self):
        self.ws.disconnect()

    # Set the current scene
    def set_scene(self, new_scene):
        self.ws.call(requests.SetCurrentProgramScene(sceneName=new_scene))

    # Set the visibility of any source's filters
    def set_filter_visibility(self, source_name, filter_name, filter_enabled=True):
        self.ws.call(requests.SetSourceFilterEnabled(sourceName=source_name, filterName=filter_name, filterEnabled=filter_enabled))

    # SAFELY set the visibility of a source
    def set_source_visibility(self, scene_name, source_name, source_visible=True):
        try:
            response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
            if 'sceneItemId' not in response.datain:
                print(f"[red]Could not find sceneItemId for {source_name} in scene {scene_name}. Response: {response.datain}")
                return
            myItemID = response.datain['sceneItemId']
            self.ws.call(requests.SetSceneItemEnabled(sceneName=scene_name, sceneItemId=myItemID, sceneItemEnabled=source_visible))
        except Exception as e:
            print(f"[red]Error setting visibility for '{source_name}' in scene '{scene_name}': {e}")

    # Returns the current text of a text source
    def get_text(self, source_name):
        response = self.ws.call(requests.GetInputSettings(inputName=source_name))
        return response.datain["inputSettings"]["text"]

    # Sets text of a text source
    def set_text(self, source_name, new_text):
        self.ws.call(requests.SetInputSettings(inputName=source_name, inputSettings={'text': new_text}))

    def get_source_transform(self, scene_name, source_name):
        response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
        myItemID = response.datain['sceneItemId']
        response = self.ws.call(requests.GetSceneItemTransform(sceneName=scene_name, sceneItemId=myItemID))
        transform = {}
        transform["positionX"] = response.datain["sceneItemTransform"]["positionX"]
        transform["positionY"] = response.datain["sceneItemTransform"]["positionY"]
        transform["scaleX"] = response.datain["sceneItemTransform"]["scaleX"]
        transform["scaleY"] = response.datain["sceneItemTransform"]["scaleY"]
        transform["rotation"] = response.datain["sceneItemTransform"]["rotation"]
        transform["sourceWidth"] = response.datain["sceneItemTransform"]["sourceWidth"]
        transform["sourceHeight"] = response.datain["sceneItemTransform"]["sourceHeight"]
        transform["width"] = response.datain["sceneItemTransform"]["width"]
        transform["height"] = response.datain["sceneItemTransform"]["height"]
        transform["cropLeft"] = response.datain["sceneItemTransform"]["cropLeft"]
        transform["cropRight"] = response.datain["sceneItemTransform"]["cropRight"]
        transform["cropTop"] = response.datain["sceneItemTransform"]["cropTop"]
        transform["cropBottom"] = response.datain["sceneItemTransform"]["cropBottom"]
        return transform

    def set_source_transform(self, scene_name, source_name, new_transform):
        response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
        myItemID = response.datain['sceneItemId']
        self.ws.call(requests.SetSceneItemTransform(sceneName=scene_name, sceneItemId=myItemID, sceneItemTransform=new_transform))

    def get_input_settings(self, input_name):
        return self.ws.call(requests.GetInputSettings(inputName=input_name))

    def get_input_kind_list(self):
        return self.ws.call(requests.GetInputKindList())

    def get_scene_items(self, scene_name):
        return self.ws.call(requests.GetSceneItemList(sceneName=scene_name))


if __name__ == '__main__':
    # Example usage
    obswebsockets_manager = OBSWebsocketsManager()

    # You can quickly test your scene and source visibility
    TEST_SCENE = "*** Mid Monitor"
    TEST_SOURCE = "Elgato Cam Link"

    obswebsockets_manager.set_source_visibility(TEST_SCENE, TEST_SOURCE, True)
    time.sleep(3)
    obswebsockets_manager.set_source_visibility(TEST_SCENE, TEST_SOURCE, False)
    time.sleep(3)
    obswebsockets_manager.disconnect()
