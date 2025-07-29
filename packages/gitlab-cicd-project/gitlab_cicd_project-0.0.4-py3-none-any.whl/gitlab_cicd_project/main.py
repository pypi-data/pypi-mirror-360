import ipywidgets as widgets
from IPython.display import display, clear_output
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import speedtest
import time
import threading
from datetime import datetime, timezone
import subprocess
import platform
import psutil
import base64
from io import BytesIO
import json

class WifiSpeedTester:
    def __init__(self):
        self.is_running = False
        self.results = []
        self.fig = None
        self.current_test_data = {}
        
        # Create widgets
        self.setup_widgets()
        self.setup_plotly_figure()
        
    def setup_widgets(self):
        """Setup all the interactive widgets"""
        # Main control buttons
        self.start_button = widgets.Button(
            description="Start Speed Test",
            button_style='success',
            icon='play',
            layout=widgets.Layout(width='150px')
        )
        
        self.stop_button = widgets.Button(
            description="Stop Test",
            button_style='danger',
            icon='stop',
            layout=widgets.Layout(width='150px'),
            disabled=True
        )
        
        self.snapshot_button = widgets.Button(
            description="Take Snapshot",
            button_style='info',
            icon='camera',
            layout=widgets.Layout(width='150px')
        )
        
        # Status display
        self.status_output = widgets.Output()
        
        # WiFi information display
        self.wifi_info_output = widgets.Output()
        
        # Speed test results display
        self.results_output = widgets.Output()
        
        # Progress bar
        self.progress_bar = widgets.FloatProgress(
            value=0,
            min=0,
            max=100,
            description='Progress:',
            bar_style='info',
            orientation='horizontal'
        )
        
        # Test interval slider
        self.interval_slider = widgets.IntSlider(
            value=5,
            min=1,
            max=30,
            step=1,
            description='Test Interval (s):',
            layout=widgets.Layout(width='300px')
        )
        
        # Plotly figure widget
        self.fig_widget = None
        
        # Bind button events
        self.start_button.on_click(self.start_test)
        self.stop_button.on_click(self.stop_test)
        self.snapshot_button.on_click(self.take_snapshot)
        
    def setup_plotly_figure(self):
        """Setup the interactive Plotly figure"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Download Speed', 'Upload Speed',
                'Ping Latency',    'Real-time Progress'
            ),
            specs=[
                [ {"type": "xy"},     {"type": "xy"} ],
                [ {"type": "xy"},     {"type": "domain"} ]
            ]
        )
        
        # Convert the regular figure to a FigureWidget
        self.fig_widget = go.FigureWidget(fig)

        
        # Add initial empty traces
        self.fig_widget.add_trace(
            go.Scatter(x=[], y=[], mode='lines+markers', name='Download'),
            row=1, col=1
        )
        
        self.fig_widget.add_trace(
            go.Scatter(x=[], y=[], mode='lines+markers', name='Upload'),
            row=1, col=2
        )
        
        self.fig_widget.add_trace(
            go.Scatter(x=[], y=[], mode='lines+markers', name='Ping'),
            row=2, col=1
        )
        
        # Real-time gauge for current test
        self.fig_widget.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=0,
                title={'text': "Current Download (Mbps)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "royalblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "red"},
                        {'range': [30, 70], 'color': "orange"},
                        {'range': [70, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                },
                domain={'x':[0,1],'y':[0,1]}
            ),
            row=2, col=2
        )

        
        self.fig_widget.update_layout(
            height=800,
            showlegend=True,
            title_text="WiFi Speed Test Dashboard",
            title_x=0.5
        )
        
    def get_wifi_info(self):
        """Get current WiFi network information"""
        wifi_info = {}
        
        try:
            # Get current datetime with timezone
            current_time = datetime.now(timezone.utc)
            wifi_info['timestamp'] = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            wifi_info['timezone'] = str(current_time.astimezone().tzinfo)
            
            # Platform-specific WiFi information
            if platform.system().lower() == "windows":
                result = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"], 
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "SSID" in line and "BSSID" not in line:
                            wifi_info['ssid'] = line.split(':')[1].strip()
                        elif "Signal" in line:
                            wifi_info['signal_strength'] = line.split(':')[1].strip()
                        elif "Channel" in line:
                            wifi_info['channel'] = line.split(':')[1].strip()
            
            elif platform.system().lower() == "linux":
                try:
                    result = subprocess.run(
                        ["iwgetid", "-r"], 
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        wifi_info['ssid'] = result.stdout.strip()
                except:
                    wifi_info['ssid'] = "Unable to detect"
            
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            for interface_name, interface_addresses in interfaces.items():
                if 'wifi' in interface_name.lower() or 'wlan' in interface_name.lower():
                    for address in interface_addresses:
                        if address.family == 2:  # IPv4
                            wifi_info['ip_address'] = address.address
                            break
            
        except Exception as e:
            wifi_info['error'] = str(e)
            
        return wifi_info
    
    def run_speed_test(self):
        """Run a single speed test"""
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            # Update progress
            self.progress_bar.value = 25
            
            # Test download speed
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            self.progress_bar.value = 50
            
            # Update real-time gauge
            with self.fig_widget.batch_update():
                self.fig_widget.data[3].value = download_speed
            
            # Test upload speed
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            self.progress_bar.value = 75
            
            # Test ping
            ping_result = st.results.ping
            self.progress_bar.value = 100
            
            return {
                'timestamp': datetime.now(),
                'download': round(download_speed, 2),
                'upload': round(upload_speed, 2),
                'ping': round(ping_result, 2),
                'server': st.results.server
            }
            
        except Exception as e:
            with self.status_output:
                print(f"Error during speed test: {e}")
            return None
    
    def update_plots(self, result):
        """Update the plotly graphs with new data"""
        if not result:
            return
            
        self.results.append(result)
        
        # Prepare data
        timestamps = [r['timestamp'] for r in self.results]
        downloads = [r['download'] for r in self.results]
        uploads = [r['upload'] for r in self.results]
        pings = [r['ping'] for r in self.results]
        
        # Update plots with batch update for smooth animation
        with self.fig_widget.batch_update():
            # Update download speed plot
            self.fig_widget.data[0].x = timestamps
            self.fig_widget.data[0].y = downloads
            
            # Update upload speed plot
            self.fig_widget.data[1].x = timestamps
            self.fig_widget.data[1].y = uploads
            
            # Update ping plot
            self.fig_widget.data[2].x = timestamps
            self.fig_widget.data[2].y = pings
            
            # Update gauge
            self.fig_widget.data[3].value = downloads[-1] if downloads else 0
    
    def continuous_testing(self):
        """Run continuous speed tests"""
        while self.is_running:
            # Display current WiFi info
            wifi_info = self.get_wifi_info()
            with self.wifi_info_output:
                clear_output()
                print("=== WiFi Network Information ===")
                for key, value in wifi_info.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
                print()
            
            # Run speed test
            with self.status_output:
                clear_output()
                print("Running speed test...")
            
            result = self.run_speed_test()
            
            if result:
                # Update plots
                self.update_plots(result)
                
                # Display results
                with self.results_output:
                    clear_output()
                    print("=== Latest Speed Test Results ===")
                    print(f"Download: {result['download']} Mbps")
                    print(f"Upload: {result['upload']} Mbps")
                    print(f"Ping: {result['ping']} ms")
                    print(f"Time: {result['timestamp'].strftime('%H:%M:%S')}")
                    if 'server' in result:
                        server_info = result['server']
                        print(f"Server: {server_info.get('sponsor', 'Unknown')} - {server_info.get('name', 'Unknown')}")
            
            # Reset progress bar
            self.progress_bar.value = 0
            
            # Wait for next test
            if self.is_running:
                time.sleep(self.interval_slider.value)
    
    def start_test(self, button):
        """Start the speed testing process"""
        if not self.is_running:
            self.is_running = True
            self.start_button.disabled = True
            self.stop_button.disabled = False
            
            with self.status_output:
                clear_output()
                print("Starting continuous speed tests...")
            
            # Start testing in a separate thread
            self.test_thread = threading.Thread(target=self.continuous_testing)
            self.test_thread.daemon = True
            self.test_thread.start()
    
    def stop_test(self, button):
        """Stop the speed testing process"""
        self.is_running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        
        with self.status_output:
            clear_output()
            print("Speed tests stopped.")
        
        self.progress_bar.value = 0
    
    def take_snapshot(self, button):
        """Take a snapshot of current results"""
        if self.results:
            # Create summary statistics
            downloads = [r['download'] for r in self.results]
            uploads = [r['upload'] for r in self.results]
            pings = [r['ping'] for r in self.results]
            
            summary = {
                'total_tests': len(self.results),
                'avg_download': round(sum(downloads) / len(downloads), 2),
                'avg_upload': round(sum(uploads) / len(uploads), 2),
                'avg_ping': round(sum(pings) / len(pings), 2),
                'max_download': max(downloads),
                'max_upload': max(uploads),
                'min_ping': min(pings),
                'snapshot_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with self.status_output:
                clear_output()
                print("=== Snapshot Summary ===")
                for key, value in summary.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
                
                # Save to JSON file
                filename = f"wifi_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump({
                        'summary': summary,
                        'detailed_results': [
                            {
                                'timestamp': r['timestamp'].isoformat(),
                                'download': r['download'],
                                'upload': r['upload'],
                                'ping': r['ping']
                            } for r in self.results
                        ]
                    }, f, indent=2)
                
                print(f"\nSnapshot saved to: {filename}")
    
    def display(self):
        """Display the complete widget interface"""
        # Control panel
        controls = widgets.HBox([
            self.start_button,
            self.stop_button,
            self.snapshot_button
        ])
        
        # Settings panel
        settings = widgets.VBox([
            self.interval_slider,
            self.progress_bar
        ])
        
        # Information panels
        info_panel = widgets.HBox([
            widgets.VBox([
                widgets.HTML("<h3>WiFi Information</h3>"),
                self.wifi_info_output
            ]),
            widgets.VBox([
                widgets.HTML("<h3>Latest Results</h3>"),
                self.results_output
            ])
        ])
        
        # Status panel
        status_panel = widgets.VBox([
            widgets.HTML("<h3>Status</h3>"),
            self.status_output
        ])
        
        # Create a widget to hold the figure
        figure_widget = widgets.Output()
        with figure_widget:
            display(self.fig_widget)
            
        # Main layout
        main_layout = widgets.VBox([
            widgets.HTML("<h1>🚀 WiFi Speed Test Dashboard</h1>"),
            controls,
            settings,
            status_panel,
            info_panel,
            widgets.HTML("<h3>Interactive Speed Charts</h3>"),
            figure_widget
        ])
        
        display(main_layout)

def hello():
    """Main function to start the WiFi speed test application"""
    print("🚀 Welcome to LDMS WiFi Speed Test Application!")
    print("Starting interactive dashboard...")
    
    # Create and display the speed tester
    speed_tester = WifiSpeedTester()
    speed_tester.display()
    
    return speed_tester

# For direct module execution
if __name__ == "__main__":
    hello()
