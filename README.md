# Wireless Plasma Stick Home Assistant control

This repo contains a basic micropython firmware, configuration files and instructions to use a [Wireless Plasma Stick](https://shop.pimoroni.com/products/wireless-plasma-kit?variant=40372594704467) with a Neopixel led strip with home assistant.

## Installing the firmware

First, grab the latest Pimoroni micropython release for their [repo](https://github.com/pimoroni/pimoroni-pico/releases) and flash it onto the plasma stick. Then open the config.py and fill the details for your WiFi and MQTT broker and topics. Finally, move copy the contents of the firmware folder onto the Pico's filesystem.
The next time you power on the device the lights will be on red for 5 seconds while connecting to the WiFi, then briefly go blue while attempting connection to the MQTT broker and, if everything goes well the light will turn off.
The lights will flash if the board couldn't connect to the WiFi (red) or MQTT broker (blue) before rebooting and attempting connection again.

## Setting up home assistant

This repo takes uses the MQTT light integration in home assistant. Open the configuration.yaml file and paste the following code in.

```
mqtt:
  light:
    - schema: json
      name: rgb_strip
      unique_id: "client_id"
      state_topic: "state_topic"
      command_topic: "state_topic/set"
      color_mode: true
      supported_color_modes: ["hs"]
      effect: true
      effect_list: ["solid","rainbow", "breathing", "fire", "pulse"]
      qos: 0
      enabled_by_default: false
```

Remember to modify the state_topic and command_topic to match the ones in config.py.
Further documentation on the MQTT light integration can be found here https://www.home-assistant.io/integrations/light.mqtt/
the final thing we will need to do is to install a custom lovelace card to control our strip, I personally use [rgb light card](https://github.com/bokub/rgb-light-card) by bokub.

## Extras

I have also included the STL for a 3D printed case to protect the plasma stick and strain relief for the screw terminal. The case needs 4 M2 x 6 mm screws.