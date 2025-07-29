# 🎛️ ACOLYTE Configuration Playground

**Una herramienta interactiva para experimentar con TODAS las configuraciones de ACOLYTE**

## 🎯 Objetivo

Crear una aplicación que permita a los usuarios:
1. Detectar su hardware automáticamente
2. Ajustar TODOS los parámetros de configuración
3. Ver en tiempo real qué es posible con su hardware
4. Exportar configuraciones óptimas
5. Comparar diferentes setups

## 🏗️ Arquitectura Propuesta

### Stack Técnico
- **Frontend**: Streamlit (rápido de desarrollar, interactivo)
- **Backend**: FastAPI (para cálculos pesados)
- **Testing**: Ollama local para pruebas reales
- **Exportación**: YAML/JSON para .acolyte

## 📊 Funcionalidades Principales

### 1. Detección de Hardware
```python
import psutil
import GPUtil
import platform
import subprocess

class HardwareDetector:
    def detect_all(self):
        return {
            "cpu": {
                "cores": psutil.cpu_count(),
                "model": platform.processor(),
                "freq_ghz": psutil.cpu_freq().max / 1000
            },
            "ram": {
                "total_gb": psutil.virtual_memory().total // (1024**3),
                "available_gb": psutil.virtual_memory().available // (1024**3),
                "speed": self.detect_ram_speed()  # Platform specific
            },
            "gpu": self.detect_gpus(),
            "disk": {
                "type": self.detect_disk_type(),  # SSD vs HDD
                "read_speed_mb": self.benchmark_disk()
            }
        }
    
    def detect_gpus(self):
        gpus = []
        for gpu in GPUtil.getGPUs():
            gpus.append({
                "name": gpu.name,
                "vram_gb": gpu.memoryTotal / 1024,
                "compute_capability": self.get_compute_capability(gpu)
            })
        return gpus
```

### 2. Configurador de Modelo
```python
# Configuración interactiva con sliders
MODEL_CONFIGS = {
    "1.5B": {
        "layers": 24,
        "base_size_gb": 3.0,
        "sizes": {
            "F16": 3.0,
            "Q8_0": 1.5,
            "Q6_K": 1.2,
            "Q5_K_M": 1.0,
            "Q4_K_M": 0.9,
            "Q4_0": 0.8,
            "Q3_K_M": 0.7,
            "Q2_K": 0.6
        }
    },
    "3B": {
        "layers": 26,
        "base_size_gb": 6.0,
        # ... más tamaños
    },
    "7B": {
        "layers": 32,
        "base_size_gb": 14.0,
        # ... más tamaños
    },
    # ... hasta 32B
}

def calculate_model_requirements(model_size, quantization, num_gpu_layers):
    config = MODEL_CONFIGS[model_size]
    model_gb = config["sizes"][quantization]
    
    # Calcular distribución GPU/CPU
    gb_per_layer = model_gb / config["layers"]
    gpu_memory = gb_per_layer * num_gpu_layers
    cpu_memory = gb_per_layer * (config["layers"] - num_gpu_layers)
    
    return {
        "gpu_required": gpu_memory,
        "ram_required": cpu_memory,
        "estimated_speed": estimate_speed(num_gpu_layers / config["layers"])
    }
```

### 3. Calculadora de Context/KV Cache
```python
def calculate_kv_cache(model_size, context_tokens, kv_quantization):
    """Calcula memoria necesaria para KV cache"""
    
    # Fórmula real de Ollama
    # kv_cache_size = 2 * n_layers * d_model * context_length * bytes_per_element
    
    MODEL_DIMS = {
        "1.5B": {"layers": 24, "d_model": 2048},
        "3B": {"layers": 26, "d_model": 3072},
        "7B": {"layers": 32, "d_model": 4096},
        "14B": {"layers": 40, "d_model": 5120},
        "32B": {"layers": 60, "d_model": 6656}
    }
    
    BYTES_PER_ELEMENT = {
        "F16": 2,      # 16-bit float
        "Q8_0": 1,     # 8-bit quantized
        "Q4_0": 0.5    # 4-bit quantized
    }
    
    dims = MODEL_DIMS[model_size]
    bytes_per = BYTES_PER_ELEMENT[kv_quantization]
    
    # Cálculo
    kv_cache_bytes = (
        2 *  # K and V
        dims["layers"] * 
        dims["d_model"] * 
        context_tokens * 
        bytes_per
    )
    
    return kv_cache_bytes / (1024**3)  # Convert to GB
```

### 4. Interfaz Principal (Streamlit)
```python
import streamlit as st
import plotly.graph_objects as go

def main():
    st.set_page_config(
        page_title="ACOLYTE Config Playground",
        page_icon="🎛️",
        layout="wide"
    )
    
    # Sidebar con hardware detectado
    with st.sidebar:
        st.header("🖥️ Hardware Detectado")
        hw = detect_hardware()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("RAM", f"{hw['ram']['total_gb']}GB")
            st.metric("CPU", f"{hw['cpu']['cores']} cores")
        with col2:
            st.metric("VRAM", f"{hw['gpu'][0]['vram_gb']}GB")
            st.metric("Disk", hw['disk']['type'])
    
    # Tabs principales
    tabs = st.tabs([
        "🤖 Modelo",
        "💾 Memoria", 
        "🔍 RAG",
        "⚡ Performance",
        "📊 Comparación",
        "💾 Exportar"
    ])
    
    with tabs[0]:
        model_configuration_tab()
    with tabs[1]:
        memory_configuration_tab()
    with tabs[2]:
        rag_configuration_tab()
    with tabs[3]:
        performance_testing_tab()
    with tabs[4]:
        comparison_tab()
    with tabs[5]:
        export_configuration_tab()
```

### 5. Tab de Configuración de Modelo
```python
def model_configuration_tab():
    st.header("🤖 Configuración de Modelo")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.subheader("Modelo Base")
        model_size = st.selectbox(
            "Tamaño", 
            ["1.5B", "3B", "7B", "14B", "32B"],
            index=2  # Default 7B
        )
        
        quantization = st.select_slider(
            "Cuantización",
            options=["F16", "Q8_0", "Q6_K", "Q5_K_M", "Q4_K_M", "Q4_0", "Q3_K_M", "Q2_K"],
            value="Q4_K_M"
        )
        
        show_quality_impact(quantization)
    
    with col2:
        st.subheader("Distribución GPU/CPU")
        
        total_layers = MODEL_CONFIGS[model_size]["layers"]
        
        # Auto-calcular máximo posible
        max_gpu_layers = calculate_max_gpu_layers(
            model_size, quantization, st.session_state.hw['gpu'][0]['vram_gb']
        )
        
        num_gpu = st.slider(
            "Capas en GPU",
            min_value=0,
            max_value=total_layers,
            value=min(max_gpu_layers, total_layers),
            help=f"Máximo recomendado: {max_gpu_layers}"
        )
        
        # Mostrar distribución visual
        show_layer_distribution(num_gpu, total_layers)
    
    with col3:
        st.subheader("📊 Resultados")
        
        # Calcular todos los requisitos
        reqs = calculate_model_requirements(model_size, quantization, num_gpu)
        
        # Métricas con colores
        gpu_color = "normal" if reqs["gpu_required"] <= st.session_state.hw['gpu'][0]['vram_gb'] else "inverse"
        ram_color = "normal" if reqs["ram_required"] <= st.session_state.hw['ram']['available_gb'] else "inverse"
        
        st.metric(
            "VRAM Necesaria",
            f"{reqs['gpu_required']:.1f}GB",
            delta=f"{st.session_state.hw['gpu'][0]['vram_gb'] - reqs['gpu_required']:.1f}GB libre",
            delta_color=gpu_color
        )
        
        st.metric(
            "RAM Necesaria",
            f"{reqs['ram_required']:.1f}GB",
            delta=f"{st.session_state.hw['ram']['available_gb'] - reqs['ram_required']:.1f}GB libre",
            delta_color=ram_color
        )
        
        st.metric(
            "Velocidad Estimada",
            f"{reqs['estimated_speed']:.1f} tok/s"
        )
```

### 6. Tab de Memoria/Context
```python
def memory_configuration_tab():
    st.header("💾 Configuración de Memoria y Context")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Context Window")
        
        # Slider logarítmico para context
        context_power = st.slider(
            "Context Size (2^n)",
            min_value=11,  # 2^11 = 2K
            max_value=17,  # 2^17 = 128K
            value=15,      # 2^15 = 32K
            format_func=lambda x: f"{2**x:,} tokens ({2**x//1024}K)"
        )
        context_size = 2 ** context_power
        
        # KV Cache Quantization
        kv_quant = st.radio(
            "KV Cache Quantization",
            ["F16", "Q8_0", "Q4_0"],
            format_func=lambda x: {
                "F16": "F16 - Sin comprimir (mejor calidad)",
                "Q8_0": "Q8_0 - 50% compresión (buena calidad)",
                "Q4_0": "Q4_0 - 66% compresión (calidad reducida)"
            }[x]
        )
        
        # Flash Attention
        use_flash = st.checkbox(
            "Usar Flash Attention",
            value=True,
            help="Reduce uso de memoria y aumenta velocidad"
        )
    
    with col2:
        st.subheader("📊 Impacto en Memoria")
        
        # Calcular KV cache para el modelo actual
        kv_cache_gb = calculate_kv_cache(
            st.session_state.model_size,
            context_size,
            kv_quant
        )
        
        # Visualización de memoria total
        memory_breakdown = {
            "Modelo": st.session_state.model_memory,
            "KV Cache": kv_cache_gb,
            "Overhead": 0.5  # Sistema
        }
        
        # Gráfico de torta
        fig = go.Figure(data=[go.Pie(
            labels=list(memory_breakdown.keys()),
            values=list(memory_breakdown.values()),
            hole=.3
        )])
        fig.update_layout(
            title=f"Uso Total: {sum(memory_breakdown.values()):.1f}GB"
        )
        st.plotly_chart(fig)
        
        # Advertencias
        total_vram_needed = sum(memory_breakdown.values())
        if total_vram_needed > st.session_state.hw['gpu'][0]['vram_gb']:
            st.error(f"⚠️ Necesitas {total_vram_needed:.1f}GB pero solo tienes {st.session_state.hw['gpu'][0]['vram_gb']}GB VRAM")
            st.info("💡 Considera: Reducir context, usar más quantización, o habilitar offloading CPU")
```

### 7. Tab de Testing en Vivo
```python
def performance_testing_tab():
    st.header("⚡ Testing de Performance en Vivo")
    
    if st.button("🚀 Ejecutar Test de Performance", type="primary"):
        with st.spinner("Creando configuración de prueba..."):
            # Crear Modelfile temporal
            modelfile = create_test_modelfile(st.session_state.current_config)
            
            # Crear modelo en Ollama
            model_name = f"acolyte-test-{int(time.time())}"
            create_ollama_model(model_name, modelfile)
            
        # Tests progresivos
        test_prompts = [
            ("Simple", "Explica qué es una variable", 100),
            ("Mediano", "Implementa una función de ordenamiento", 500),
            ("Complejo", "Crea una API REST completa", 2000),
            ("Context largo", "Analiza este código: " + get_sample_code(), 5000)
        ]
        
        results = []
        progress = st.progress(0)
        
        for i, (test_name, prompt, expected_tokens) in enumerate(test_prompts):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Test**: {test_name}")
            
            with col2:
                start = time.time()
                response = run_ollama_test(model_name, prompt)
                elapsed = time.time() - start
                
                tokens = count_tokens(response)
                speed = tokens / elapsed
                
                st.metric("Velocidad", f"{speed:.1f} tok/s")
            
            with col3:
                st.metric("Tiempo", f"{elapsed:.1f}s")
                st.metric("Tokens", tokens)
            
            results.append({
                "test": test_name,
                "speed": speed,
                "time": elapsed,
                "tokens": tokens
            })
            
            progress.progress((i + 1) / len(test_prompts))
        
        # Mostrar resumen
        show_performance_summary(results)
        
        # Limpiar modelo de prueba
        cleanup_test_model(model_name)
```

### 8. Tab de Comparación
```python
def comparison_tab():
    st.header("📊 Comparación de Configuraciones")
    
    # Permitir guardar múltiples configuraciones
    col1, col2 = st.columns([3, 1])
    
    with col1:
        config_name = st.text_input("Nombre de configuración")
    with col2:
        if st.button("💾 Guardar Actual"):
            save_configuration(config_name)
    
    # Mostrar configuraciones guardadas
    if st.session_state.saved_configs:
        selected = st.multiselect(
            "Selecciona configuraciones para comparar",
            list(st.session_state.saved_configs.keys())
        )
        
        if selected:
            # Crear tabla comparativa
            comparison_df = create_comparison_table(selected)
            st.dataframe(
                comparison_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Gráficos comparativos
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de velocidad vs memoria
                fig = create_speed_vs_memory_chart(selected)
                st.plotly_chart(fig)
            
            with col2:
                # Gráfico de calidad vs costo
                fig = create_quality_vs_cost_chart(selected)
                st.plotly_chart(fig)
```

### 9. Tab de Exportación
```python
def export_configuration_tab():
    st.header("💾 Exportar Configuración")
    
    # Vista previa de la configuración actual
    st.subheader("Configuración Actual")
    
    config = generate_acolyte_config(st.session_state.current_config)
    
    # Mostrar en YAML con syntax highlighting
    st.code(yaml.dump(config, default_flow_style=False), language="yaml")
    
    # Opciones de exportación
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.download_button(
            "📥 Descargar .acolyte",
            data=yaml.dump(config),
            file_name=".acolyte",
            mime="text/yaml"
        ):
            st.success("✅ Descargado!")
    
    with col2:
        if st.button("📋 Copiar al portapapeles"):
            pyperclip.copy(yaml.dump(config))
            st.success("✅ Copiado!")
    
    with col3:
        if st.button("🚀 Aplicar a ACOLYTE"):
            apply_configuration(config)
            st.success("✅ Configuración aplicada!")
    
    # Generar script de inicio
    st.subheader("Script de Inicio Personalizado")
    
    startup_script = generate_startup_script(config)
    st.code(startup_script, language="bash")
```

## 🎮 Características Avanzadas

### 1. Modo "Auto-Optimize"
```python
def auto_optimize():
    """Encuentra la mejor configuración para el hardware actual"""
    
    hardware = detect_hardware()
    
    # Definir objetivos
    objectives = st.multiselect(
        "¿Qué es más importante?",
        ["Velocidad", "Calidad", "Context largo", "Ahorro de recursos"],
        default=["Velocidad", "Calidad"]
    )
    
    # Algoritmo de optimización
    configs = generate_candidate_configs(hardware)
    scores = []
    
    for config in configs:
        score = evaluate_config(config, objectives, hardware)
        scores.append((score, config))
    
    # Mostrar top 3
    best_configs = sorted(scores, reverse=True)[:3]
    
    for i, (score, config) in enumerate(best_configs):
        with st.expander(f"Opción {i+1} - Score: {score:.2f}"):
            show_config_details(config)
```

### 2. Simulador de Carga
```python
def workload_simulator():
    """Simula diferentes cargas de trabajo"""
    
    workloads = {
        "Chat casual": {
            "avg_context": 4000,
            "response_length": 500,
            "frequency": "baja"
        },
        "Desarrollo activo": {
            "avg_context": 20000,
            "response_length": 2000,
            "frequency": "alta"
        },
        "Code review": {
            "avg_context": 30000,
            "response_length": 3000,
            "frequency": "media"
        },
        "Refactoring masivo": {
            "avg_context": 50000,
            "response_length": 5000,
            "frequency": "burst"
        }
    }
    
    selected_workload = st.selectbox("Tipo de trabajo", list(workloads.keys()))
    
    # Simular y mostrar resultados
    results = simulate_workload(
        workloads[selected_workload],
        st.session_state.current_config
    )
    
    show_simulation_results(results)
```

### 3. Calculadora de Costos (para cloud)
```python
def cloud_cost_calculator():
    """Calcula costos si usas GPU cloud"""
    
    providers = {
        "RunPod": {
            "RTX 4090": 0.74,
            "RTX A6000": 0.79,
            "A100 40GB": 1.09,
            "H100 80GB": 2.49
        },
        "Vast.ai": {
            "RTX 4090": 0.50,
            "RTX A6000": 0.65,
            "A100 40GB": 0.80,
            "H100 80GB": 2.00
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        provider = st.selectbox("Proveedor", list(providers.keys()))
        gpu_type = st.selectbox("GPU", list(providers[provider].keys()))
        hours_per_day = st.slider("Horas/día", 1, 24, 8)
        days_per_month = st.slider("Días/mes", 1, 30, 20)
    
    with col2:
        hourly_cost = providers[provider][gpu_type]
        daily_cost = hourly_cost * hours_per_day
        monthly_cost = daily_cost * days_per_month
        
        st.metric("Costo por hora", f"${hourly_cost:.2f}")
        st.metric("Costo diario", f"${daily_cost:.2f}")
        st.metric("Costo mensual", f"${monthly_cost:.2f}")
        
        # Comparar con hardware local
        local_gpu_price = estimate_gpu_price(gpu_type)
        payback_months = local_gpu_price / monthly_cost
        
        st.info(f"💡 Comprar una {gpu_type} (~${local_gpu_price}) se paga en {payback_months:.1f} meses")
```

## 🚀 Instalación y Uso

```bash
# Instalar dependencias
pip install streamlit plotly psutil gputil pyyaml ollama

# Ejecutar
streamlit run acolyte_playground.py

# O con Docker
docker run -p 8501:8501 acolyte/playground
```

## 📈 Beneficios

1. **Transparencia Total**: Los usuarios ven EXACTAMENTE qué pueden hacer con su hardware
2. **Experimentación Segura**: Prueban configuraciones sin romper nada
3. **Educativo**: Entienden cómo cada parámetro afecta el rendimiento
4. **Optimización Real**: Encuentran la configuración ÓPTIMA para su caso
5. **Comparación Objetiva**: Ven si vale la pena actualizar hardware o usar cloud

## 🎯 Conclusión

Con esta herramienta, ACOLYTE se vuelve **verdaderamente accesible para todos** porque:

- **Principiantes**: Ven qué es posible y aprenden
- **Intermedios**: Optimizan su configuración actual
- **Avanzados**: Experimentan con configuraciones extremas
- **Sin GPU**: Ven exactamente cuánto costaría usar cloud

**Es la transparencia y flexibilidad que ACOLYTE necesita para ser universal** 🌍