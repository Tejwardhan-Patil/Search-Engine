package main

import (
	"log"
	"net/http"
	"runtime"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// SystemMetricsCollector defines a struct for the custom Prometheus metrics collector
type SystemMetricsCollector struct {
	cpuUsage    *prometheus.Desc
	memoryUsage *prometheus.Desc
	goRoutines  *prometheus.Desc
}

// NewSystemMetricsCollector initializes the custom metrics
func NewSystemMetricsCollector() *SystemMetricsCollector {
	return &SystemMetricsCollector{
		cpuUsage:    prometheus.NewDesc("system_cpu_usage_percentage", "Current CPU usage in percentage", nil, nil),
		memoryUsage: prometheus.NewDesc("system_memory_usage_bytes", "Current memory usage in bytes", nil, nil),
		goRoutines:  prometheus.NewDesc("system_goroutines_count", "Number of active Go routines", nil, nil),
	}
}

// Describe sends the descriptors of the metrics to Prometheus
func (collector *SystemMetricsCollector) Describe(ch chan<- *prometheus.Desc) {
	ch <- collector.cpuUsage
	ch <- collector.memoryUsage
	ch <- collector.goRoutines
}

// Collect fetches the system metrics and sends them to Prometheus
func (collector *SystemMetricsCollector) Collect(ch chan<- prometheus.Metric) {
	// Simulated CPU and memory usage
	cpu := getCPUUsage()
	memory := getMemoryUsage()
	goRoutines := runtime.NumGoroutine()

	ch <- prometheus.MustNewConstMetric(collector.cpuUsage, prometheus.GaugeValue, cpu)
	ch <- prometheus.MustNewConstMetric(collector.memoryUsage, prometheus.GaugeValue, memory)
	ch <- prometheus.MustNewConstMetric(collector.goRoutines, prometheus.GaugeValue, float64(goRoutines))
}

// getCPUUsage simulates the CPU usage percentage
func getCPUUsage() float64 {
	return float64(runtime.NumCPU()) * 12.5 // Simulated CPU usage logic
}

// getMemoryUsage simulates the current memory usage in bytes
func getMemoryUsage() float64 {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)
	return float64(memStats.Alloc)
}

func main() {
	// Create a new instance of the collector
	collector := NewSystemMetricsCollector()

	// Register the custom collector with Prometheus
	prometheus.MustRegister(collector)

	// Expose the /metrics endpoint for Prometheus scraping
	http.Handle("/metrics", promhttp.Handler())

	// Start HTTP server for Prometheus metrics
	server := &http.Server{
		Addr:              ":8080",
		ReadHeaderTimeout: 5 * time.Second,
	}

	log.Println("Prometheus metrics exporter running on :8080/metrics")
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("Error starting HTTP server: %v", err)
	}
}

// To simulate CPU metrics, you may use this utility function to add some CPU load
func consumeCPU(duration time.Duration) {
	end := time.Now().Add(duration)
	for time.Now().Before(end) {
		_ = getCPUUsage()
	}
}

// init initializes the CPU and memory load simulation
func init() {
	go func() {
		for {
			consumeCPU(2 * time.Second)
			time.Sleep(3 * time.Second)
		}
	}()
}
