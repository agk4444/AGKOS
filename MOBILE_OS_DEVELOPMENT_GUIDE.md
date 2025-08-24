# AGK Mobile OS Development Guide

## Overview
AGK (Advanced Game Kit) now supports comprehensive mobile OS development with native Android and iOS capabilities. This guide covers all the mobile-specific features, libraries, and tools available for building cross-platform mobile applications.

## Key Features

### 1. ARM/ARM64 Backend Support
- **Enhanced C Backend**: Extended support for ARM and ARM64 architectures
- **Mobile Build System**: Specialized build system for mobile platforms
- **Cross-Compilation**: Full Android NDK and iOS toolchain integration

### 2. Mobile Hardware Abstraction
- **Device Information**: Access to device model, OS version, screen specs
- **Battery Management**: Monitor battery level, temperature, charging status
- **CPU/GPU Monitoring**: Performance monitoring and thermal management
- **Memory Management**: Available memory and usage tracking

### 3. Mobile UI and Gesture Framework
- **Touch Components**: Buttons, text inputs, sliders, lists
- **Gesture Recognition**: Tap, swipe, pinch, rotate gestures
- **Visual Feedback**: Touch animations and haptic feedback
- **Responsive Design**: Screen density and orientation handling

### 4. Power Management
- **Performance Profiles**: High performance, balanced, power saver modes
- **Wake Locks**: Screen and CPU wake lock management
- **Thermal Throttling**: Automatic performance adjustment
- **Battery Optimization**: Smart charging and power saving tips

### 5. Mobile-Specific Templates
- **Android Template**: Native Android app with Material Design
- **iOS Template**: Native iOS app with UIKit integration
- **Cross-Platform**: Single codebase for both platforms

### 6. Mobile Networking
- **WiFi Management**: Network scanning and connection
- **Bluetooth**: Device discovery and pairing
- **NFC**: Tag reading and writing
- **VPN Support**: Secure network connections

### 7. Advanced Sensors and GPS
- **Motion Sensors**: Accelerometer, gyroscope, magnetometer
- **Environmental**: Pressure, temperature, humidity, light
- **Location Services**: GPS with high accuracy
- **Activity Recognition**: Walking, running, driving detection

### 8. Mobile App Framework
- **Component System**: Reusable UI components
- **Lifecycle Management**: App state and navigation
- **Data Persistence**: Local database and preferences
- **Permissions**: Runtime permission management

### 9. Cross-Platform Compilation
- **Android APK Generation**: Complete APK building pipeline
- **iOS IPA Generation**: Full IPA creation with provisioning
- **Automated Toolchains**: NDK and Xcode integration

## Libraries Overview

### Core Libraries

#### `mobile.agk` - Hardware Access
```agk
import mobile

// Device information
device_model = mobile.get_device_model()
battery_level = mobile.get_battery_level()

// Sensors
accelerometer_data = mobile.get_accelerometer_data()
gps_location = mobile.get_gps_location()

// Permissions
mobile.request_location_permission()
```

#### `mobile_ui.agk` - User Interface
```agk
import mobile_ui
import graphics

// Create UI components
button = mobile_ui.create_button(50, 100, 200, 50, "Click Me")
mobile_ui.draw_button(canvas, button)

// Gesture handling
gesture = mobile_ui.detect_gesture()
if gesture == mobile_ui.GESTURE_SWIPE_LEFT:
    // Handle swipe
```

#### `power.agk` - Power Management
```agk
import power

// Performance control
power.set_performance_profile(power.PERF_PROFILE_BALANCED)
power.request_wake_lock(power.WAKE_LOCK_SCREEN)

// Battery monitoring
battery_level = power.get_battery_level()
power_optimization_tips = power.get_battery_optimization_tips()
```

#### `mobile_network.agk` - Networking
```agk
import mobile_network

// WiFi management
mobile_network.scan_wifi_networks()
mobile_network.connect_to_wifi("MyNetwork", "password")

// Bluetooth
mobile_network.enable_bluetooth()
devices = mobile_network.scan_bluetooth_devices()
```

#### `mobile_app_framework.agk` - App Framework
```agk
import mobile_app_framework

// Create app
app = create_mobile_app("MyApp", "com.example.myapp")
on_app_create(app)

// Screen management
screen = create_screen("home", "main_layout")
navigate_to_screen(app, "home")
```

## Building Mobile Apps

### Android Development

#### 1. Setup Android NDK
```bash
# Set NDK path in build system
mobile_build.set_ndk_path("/opt/android-ndk")
mobile_build.set_sdk_path("/opt/android-sdk")
mobile_build.set_api_level(29)
```

#### 2. Configure Build System
```python
from agk_c_build import MobileBuildSystem

mobile_build = MobileBuildSystem("MyAndroidApp")
mobile_build.set_target_platform("android")
mobile_build.set_target_arch("arm64")
mobile_build.set_api_level(29)
```

#### 3. Build APK
```bash
# Generate mobile makefile
make apk

# This creates:
# - AndroidManifest.xml
# - Native library (libMyAndroidApp.so)
# - MyAndroidApp.apk
```

### iOS Development

#### 1. Setup iOS Toolchain
```bash
# iOS builds require macOS with Xcode
# Install command line tools
xcode-select --install
```

#### 2. Configure iOS Build
```python
mobile_build = MobileBuildSystem("MyIOSApp")
mobile_build.set_target_platform("ios")
mobile_build.set_target_arch("arm64")
```

#### 3. Build IPA
```bash
# Generate iOS makefile
make ipa

# This creates:
# - Info.plist
# - MyIOSApp executable
# - MyIOSApp.ipa
```

## Sample Applications

### Basic Android App
```agk
# android_app_template.agk
import graphics
import mobile
import mobile_ui
import power

main:
    # Initialize Android app
    window = graphics.create_window(mobile.get_screen_width_px(), mobile.get_screen_height_px(), "My Android App")
    canvas = graphics.create_canvas(mobile.get_screen_width_px(), mobile.get_screen_height_px())

    # Main app loop
    while true:
        # Handle touch input
        touch_events = graphics.handle_mouse_events(window)
        if touch_events:
            # Process touch events
            mobile_ui.add_touch_point(touch_events["x"], touch_events["y"], 1.0)
            gesture = mobile_ui.detect_gesture()

        # Draw UI
        graphics.draw_rectangle(canvas, 0, 0, mobile.get_screen_width_px(), mobile.get_screen_height_px(), graphics.color_white(), true)

        # Display device info
        graphics.draw_text(canvas, 20, 50, "Device: " + mobile.get_device_model(), graphics.color_black(), 16)
        graphics.draw_text(canvas, 20, 80, "Battery: " + string.format(power.get_battery_level() * 100) + "%", graphics.color_black(), 16)
```

### Basic iOS App
```agk
# ios_app_template.agk
import graphics
import mobile
import mobile_ui
import power

main:
    # Initialize iOS app
    window = graphics.create_window(mobile.get_screen_width_px(), mobile.get_screen_height_px(), "My iOS App")
    canvas = graphics.create_canvas(mobile.get_screen_width_px(), mobile.get_screen_height_px())

    # Main app loop
    while true:
        # Handle iOS-specific features
        if mobile.has_face_recognition():
            graphics.draw_text(canvas, 20, 50, "Face ID Available", graphics.color_green(), 16)

        # Draw iOS-style UI
        graphics.draw_rectangle(canvas, 0, 0, mobile.get_screen_width_px(), mobile.get_screen_height_px(), graphics.color_white(), true)

        # Display iOS-specific info
        graphics.draw_text(canvas, 20, 50, "iOS Version: " + mobile.get_os_version(), graphics.color_black(), 16)
```

## Advanced Features

### Sensor Data Recording
```agk
// Start recording accelerometer data
recording_session = mobile.start_sensor_recording(mobile.SENSOR_TYPE_ACCELEROMETER)

// Record for 30 seconds
delay(30000)

// Stop recording and save
mobile.stop_sensor_recording(recording_session)
mobile.save_sensor_data_to_file(recording_session, "accelerometer_data.csv")
```

### Geofencing
```agk
// Add geofence
geofence_id = mobile.add_geofence(37.7749, -122.4194, 100.0, "San Francisco")

// Monitor geofence events
// (events handled through callbacks)
```

### Background Tasks
```agk
// Schedule background location updates
task_id = power.schedule_background_task("location_update", 300000, "update_location")

// Cancel task
power.cancel_background_task(task_id)
```

### Push Notifications
```agk
// Initialize notifications
mobile_app_framework.initialize_push_notifications(app)

// Get device token
push_token = mobile_app_framework.get_push_token(app)
```

## Performance Optimization

### Battery Optimization
```agk
// Enable battery optimization
power.set_performance_profile(power.PERF_PROFILE_POWER_SAVER)
power.optimize_network_for_battery()

// Monitor power usage
power_session = power.start_power_monitoring()
power_usage = power.get_app_power_usage()
power.stop_power_monitoring(power_session)
```

### Memory Management
```agk
// Monitor memory usage
available_memory = mobile.get_available_memory()
memory_usage = mobile.get_memory_usage()

// Optimize memory
if memory_usage > 0.8:
    power.optimize_memory_usage()
```

## Best Practices

### 1. Permission Management
```agk
// Request permissions at appropriate times
if mobile.has_gps():
    mobile.request_location_permission()

// Check permission status
if mobile.is_location_permission_granted():
    location = mobile.get_gps_location()
```

### 2. Battery Awareness
```agk
// Adapt behavior based on battery level
battery_level = power.get_battery_level()
if battery_level < 0.2:
    power.set_performance_profile(power.PERF_PROFILE_ULTRA_LOW)
    // Reduce update rates, disable non-essential features
```

### 3. Network Efficiency
```agk
// Use appropriate network monitoring
mobile_network.set_network_callback("network_connected", "on_network_connected")
mobile_network.set_network_callback("network_disconnected", "on_network_disconnected")

// Optimize data usage
mobile_network.set_data_usage_limit(100 * 1024 * 1024)  // 100MB limit
```

### 4. Cross-Platform Compatibility
```agk
// Handle platform differences
if mobile.get_os_version() contains "Android":
    // Android-specific code
else if mobile.get_os_version() contains "iOS":
    // iOS-specific code

// Use mobile_app_framework for cross-platform components
```

## Troubleshooting

### Common Issues

#### 1. Build Failures
- **Android**: Ensure NDK path is correct and API level is supported
- **iOS**: Must build on macOS with Xcode command line tools
- **Missing Libraries**: Check that all required libraries are linked

#### 2. Permission Errors
- Request permissions at runtime, not just in manifest
- Handle permission denials gracefully
- Explain why permissions are needed

#### 3. Performance Issues
- Use appropriate performance profiles
- Monitor thermal status
- Implement background task management

#### 4. Network Issues
- Handle network state changes
- Implement retry logic for failed requests
- Respect data usage limits

## API Reference

### Mobile Hardware API
- `mobile.get_device_model()` - Get device model string
- `mobile.get_battery_level()` - Get battery level (0.0-1.0)
- `mobile.get_accelerometer_data()` - Get accelerometer [x,y,z]
- `mobile.get_gps_location()` - Get GPS [lat, lon, alt]
- `mobile.vibrate_device(duration)` - Vibrate device

### Power Management API
- `power.set_performance_profile(profile)` - Set performance mode
- `power.request_wake_lock(type)` - Request wake lock
- `power.get_battery_level()` - Get battery level
- `power.get_thermal_status()` - Get thermal status

### Mobile UI API
- `mobile_ui.create_button(x,y,w,h,text)` - Create button
- `mobile_ui.detect_gesture()` - Detect touch gesture
- `mobile_ui.draw_button(canvas, button)` - Draw button

### Mobile Network API
- `mobile_network.scan_wifi_networks()` - Scan WiFi networks
- `mobile_network.connect_to_wifi(ssid, pass)` - Connect to WiFi
- `mobile_network.enable_bluetooth()` - Enable Bluetooth

### Mobile App Framework API
- `create_mobile_app(name, package)` - Create app instance
- `navigate_to_screen(app, screen)` - Navigate to screen
- `request_app_permissions(app, perms)` - Request permissions

## Conclusion

The AGK Mobile OS Development capabilities provide a comprehensive platform for building cross-platform mobile applications with native performance and features. The combination of hardware access, UI frameworks, networking, and build tools enables developers to create sophisticated mobile apps using the natural language syntax of AGK.

For more examples and advanced usage patterns, see the template files:
- `android_app_template.agk`
- `ios_app_template.agk`
- `mobile_app_template.agk`