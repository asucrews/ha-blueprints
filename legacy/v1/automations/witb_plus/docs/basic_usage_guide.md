
# How to Use WITB+ Blueprint Basic Usage Guide

## Prerequisites

Before you start, make sure you have the following sensors and entities set up in your Home Assistant instance:

1. **Door Sensor**: A binary sensor or sensor group that detects the state (open/closed) of the door.
2. **Motion Sensor**: A binary sensor or sensor group that detects motion within the designated area.
3. **Light Source**: A light entity like a smart bulb, light switch, or light group.

## Things to Think About

1. Keep in mind the principle behind the "wasp in the box".  With this in mind, you're using door sensor(s) and motion sensor(s) to control light source(s); meaning, turning on, turning off, and keeping on if there's motion or the door is closed.
2. What light source are you using?
   - If it is a smart bulb, use "**Smart Light Bulb** or **Smart Light Bulb Group**" Field.
   - If it is a light switch, use "**Light**, **Light Group**, **Switch**, or **Switch Group**" Field.
3. Leave all other fields as defult settings.

## Step-by-Step Guide

1. **Access the Imported Blueprint**
   - Go to Configuration > Blueprints.
   - Find "WITB+ Stable (0.3.3)" in your list of blueprints.

2. **Create an Automation Using the Blueprint**
   - Click on the "WITB+ Stable (0.3.3)" blueprint.
   - Click on "Create Automation".

3. **Fill in the Required Fields**
   - **Door Sensor**: Select your door sensor entity from the dropdown.
   - **Motion Sensor**: Select your motion sensor entity from the dropdown.
   - **Light Source**: Select the light entity, like a smart bulb or light switch.

4. **Save and Activate the Automation**
   - Give your automation a name.
   - Click "Save".
   - Ensure the automation is toggled on to activate it.

## Example Configuration

Here is an example configuration for the automation:

```yaml
alias: Occupancy Detection
description: Automation for detecting occupancy using WITB+ blueprint.
use_blueprint:
  path: asucrews/ha-blueprints/witb_plus.yaml
  input:
    door_sensor: binary_sensor.door
    motion_sensor: binary_sensor.motion
    light_switch: light.living_room
```

## Monitoring and Adjusting the Automation

1. **Check Automation Status**
   - Go to Configuration > Automations.
   - Ensure your occupancy detection automation is active.

2. **Monitor Entities**
   - **Door Sensor**: Ensure it accurately reflects the door state (open/closed).
   - **Motion Sensor**: Verify it detects motion within the designated area.
   - **Light Source**: Check that the light source responds correctly to the automation triggers.

3. **Adjust as Needed**
   - If the automation is not behaving as expected, revisit the blueprint configuration and ensure all fields are correctly set.
   - Adjust the positions of your motion and door sensors for optimal detection.

## Troubleshooting

- **Sensor Not Detected**: Ensure that the sensors are correctly added to Home Assistant and reporting states.
- **Automation Not Triggering**: Check the conditions and triggers in the blueprint. Make sure they align with your expected setup.
- **Light Source Issues**: Verify that the light entity is correctly configured and responds to the automation.

By following these steps, you should be able to successfully use the WITB+ blueprint to manage occupancy detection in your designated area.
