import plotly.express as px  # pip install plotly-express
import plotly.graph_objs as go
import streamlit as st  # pip install streamlit
import custom_functions
import pandas as pd
import numpy as np
import warnings
import time

######################
# Page Config
######################
st.set_page_config(page_title="Nutanix Collector Analyse", page_icon='favicon.ico', layout="wide")
hide_streamlit_style = """
            <style>
            header {visibility: hidden;}
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            table td:nth-child(1) {display: none}
            table th:nth-child(1) {display: none}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
filter_form_submitted = False
warnings.simplefilter("ignore") # Ignore openpyxl Excile File Warning while reading (no default style)

######################
# Page sections
######################

header_section = st.container() # Description of page & what it is about
uploaded_file_valid = False
upload_filter_section = st.container()
analysis_section = st.container() # Content of page - either error message if wrong excel file or analysis content
sizing_section = st.container()

######################
# Page content
######################

with header_section:
    st.markdown("<h1 style='text-align: left; color:#034ea2;'>Nutanix Collector Analyse</h1>", unsafe_allow_html=True)
    st.markdown('Ein Hobby-Projekt von [**Martin Stenke**](https://www.linkedin.com/in/mstenke/) zur einfachen Analyse einer Nutanix Collector Auswertung.')
    st.info('***Disclaimer: Hierbei handelt es sich lediglich um ein Hobby Projekt - keine Garantie auf Vollständigkeit oder Korrektheit der Auswertung / Daten.***')
    st.markdown("---")

with upload_filter_section:
    st.markdown('### **Upload & Filter**')
    column_upload, column_filter = st.columns(2)
            
    with column_upload:
        uploaded_file = st.file_uploader(label="Laden Sie Ihre Excel basierte Collector Auswertung hier hoch.", type=['xlsx'])

    with column_filter:
        if uploaded_file is not None:
            try:
                # load excel, filter our relevant tabs and columns, merge all in one dataframe
                df_vInfo, df_vCPU, df_vMemory, df_vHosts, df_vCluster, df_vPartition, df_vmList = custom_functions.get_data_from_excel(uploaded_file)            

                vCluster_selected = st.multiselect(
                    "vCluster selektieren:",
                    options=sorted(df_vInfo["Cluster Name"].unique()),
                    default=sorted(df_vInfo["Cluster Name"].unique())
                )
                uploaded_file_valid = True
                st.success("Die Nutanix Collector Auswertung wurde erfolgreich hochgeladen, bitte wenden Sie die Filter an und starten Sie die Auswertung.")

            except Exception as e:
                uploaded_file_valid = False
                analysis_section.error("##### FEHLER: Die hochgeladene Excel Datei konnte leider nicht ausgelesen werden.")
                analysis_section.markdown("Im folgenden die genaue Fehlermeldung für ein Troubleshooting:")
                analysis_section.exception(e)

if uploaded_file is not None and uploaded_file_valid is True:

    with analysis_section: 

        st.markdown("---")
        st.markdown('### Auswertung')
        
        # Declare new df for filtered vCluster selection
        df_vInfo_filtered = df_vInfo.query("`Cluster Name`==@vCluster_selected")
        df_vCPU_filtered = df_vCPU.query("`Cluster Name`==@vCluster_selected")
        df_vMemory_filtered = df_vMemory.query("`Cluster Name`==@vCluster_selected")
        df_vHosts_filtered = df_vHosts.query("`Cluster Name`==@vCluster_selected")
        df_vCluster_filtered = df_vCluster.query("`Cluster Name`==@vCluster_selected")
        df_vPartition_filtered = df_vPartition.query("`Cluster Name`==@vCluster_selected")
        df_vmList_filtered = df_vmList.query("`Cluster Name`==@vCluster_selected")

        # Set bar chart setting to static for both  charts
        chart_config = {'staticPlot': True}
        chart_marker_colors = ['#034EA2','#BBE3F3']
        
        vCluster_expander = st.expander(label='vCluster Übersicht')
        with vCluster_expander:
            st.markdown(f"<h4 style='text-align: center;'>Die Auswertung umfasst <b>{ df_vCluster_filtered['Datacenter'].nunique() } Rechenzentren</b>, <b>{ df_vCluster_filtered['Cluster Name'].nunique() } Cluster</b>, <b>{ df_vHosts_filtered['Cluster Name'].shape[0] } Host</b> und <b>{ df_vInfo_filtered.shape[0] } VMs</b>.</h4>", unsafe_allow_html=True)

            column_cpu, column_memory, column_storage = st.columns(3)
            
            with column_cpu:
                st.markdown("<h4 style='text-align: center; color:#034ea2;'>pCPU:</h4>", unsafe_allow_html=True)

                total_ghz, consumed_ghz, cpu_percentage = custom_functions.generate_CPU_infos(df_vHosts_filtered)

                donut_chart_cpu = go.Figure(data = go.Pie(values = cpu_percentage, hole = 0.9, marker_colors=chart_marker_colors, sort=False,textinfo='none', hoverinfo='skip'))
                donut_chart_cpu.add_annotation(x= 0.5, y = 0.5, text = str(round(cpu_percentage[0],2))+' %',
                                    font = dict(size=20,family='Arial Black', color='black'), showarrow = False)
                donut_chart_cpu.update(layout_showlegend=False)
                donut_chart_cpu.update_layout(margin=dict(l=10, r=10, t=10, b=10,pad=4), autosize=True, height = 150)

                st.plotly_chart(donut_chart_cpu, use_container_width=True, config=chart_config)
                st.markdown(f"<p style='text-align: center;'>{consumed_ghz} GHz verwendet</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center;'>{total_ghz} GHz verfügbar</p>", unsafe_allow_html=True)                

            with column_memory:
                st.markdown("<h4 style='text-align: center; color:#034ea2;'>pMemory:</h4>", unsafe_allow_html=True)

                total_memory, consumed_memory, memory_percentage = custom_functions.generate_Memory_infos(df_vHosts_filtered)

                donut_chart_memory = go.Figure(data = go.Pie(values = memory_percentage, hole = 0.9, marker_colors=chart_marker_colors, sort=False,textinfo='none', hoverinfo='skip'))
                donut_chart_memory.add_annotation(x= 0.5, y = 0.5, text = str(round(memory_percentage[0],2))+' %',
                                    font = dict(size=20,family='Arial Black', color='black'), showarrow = False)
                donut_chart_memory.update(layout_showlegend=False)
                donut_chart_memory.update_layout(margin=dict(l=10, r=10, t=10, b=10,pad=4), autosize=True, height = 150)

                st.plotly_chart(donut_chart_memory, use_container_width=True, config=chart_config)
                st.markdown(f"<p style='text-align: center;'>{consumed_memory} GiB verwendet</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center;'>{total_memory} GiB verfügbar</p>", unsafe_allow_html=True)                

            with column_storage:
                st.markdown("<h4 style='text-align: center; color:#034ea2;'>vStorage:</h4>", unsafe_allow_html=True)

                storage_provisioned, storage_consumed, storage_percentage = custom_functions.generate_Storage_infos(df_vPartition_filtered)

                donut_chart_storage = go.Figure(data = go.Pie(values = storage_percentage, hole = 0.9, marker_colors=chart_marker_colors, sort=False,textinfo='none', hoverinfo='skip'))
                donut_chart_storage.add_annotation(x= 0.5, y = 0.5, text = str(round(storage_percentage[0],2))+' %',
                                    font = dict(size=20,family='Arial Black', color='black'), showarrow = False)
                donut_chart_storage.update(layout_showlegend=False)
                donut_chart_storage.update_layout(margin=dict(l=10, r=10, t=10, b=10,pad=4), autosize=True, height = 150)

                st.plotly_chart(donut_chart_storage, use_container_width=True, config=chart_config)
                st.markdown(f"<p style='text-align: center;'>{storage_consumed} TiB verwendet</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center;'>{storage_provisioned} TiB zugewiesen</p>", unsafe_allow_html=True)
                
            st.write('---')

            column_IOPS, column_read_write_ratio = st.columns(2)
            with column_IOPS:
                    st.markdown("<h4 style='text-align: center; color:#034ea2;'>IOPS:</h4>", unsafe_allow_html=True)
                    st.markdown(f"<h5 style='text-align: center;'>{round(df_vCluster_filtered['95th Percentile IOPS'].sum(),2)}</h5>", unsafe_allow_html=True)
            with column_read_write_ratio:
                    read_ratio, write_ratio = custom_functions.generate_read_write_ratio_infos(df_vCluster_filtered)
                    st.markdown("<h4 style='text-align: center; color:#034ea2;'>Read / Write Verhältnis:</h4>", unsafe_allow_html=True)
                    st.markdown(f"<h5 style='text-align: center;'>{read_ratio} % / {write_ratio} %</h5>", unsafe_allow_html=True)
            
            

        vHosts_expander = st.expander(label='vHosts Details')
        with vHosts_expander:
            
            hardware_df, pCPU_df, memory_df = custom_functions.generate_vHosts_overview_df(df_vHosts_filtered)
            
            column_hardware, column_pCPU, column_pRAM = st.columns(3)
            with column_hardware:
                st.markdown("<h5 style='text-align: center; color:#034ea2;'>vHost Details:</h5>", unsafe_allow_html=True)
                st.table(hardware_df)
            with column_pCPU:
                st.markdown("<h5 style='text-align: center; color:#034ea2;'>pCPU Details:</h5>", unsafe_allow_html=True)
                st.table(pCPU_df)
            with column_pRAM:
                st.markdown("<h5 style='text-align: center; color:#034ea2;'> pMemory Details:</h5>", unsafe_allow_html=True)
                st.table(memory_df)
            
            
                
        VM_expander = st.expander(label='VM Details')
        with VM_expander:

            df_vInfo_filtered_vm_on = df_vInfo_filtered.query("`Power State`=='poweredOn'")    
            df_vInfo_filtered_vm_off = df_vInfo_filtered.query("`Power State`=='poweredOff'")

            column_vm_on, column_vm_off, column_vm_total = st.columns(3)            

            with column_vm_on:                    
                st.markdown(f"<h5 style='text-align: center; color:#034ea2;'>VMs On: { df_vInfo_filtered_vm_on['MOID'].shape[0] }</h5>", unsafe_allow_html=True)

            with column_vm_off:                
                st.markdown(f"<h5 style='text-align: center; color:#034ea2;'>VMs Off: { df_vInfo_filtered_vm_off['MOID'].shape[0] }</h5>", unsafe_allow_html=True)

            with column_vm_total:
                st.markdown(f"<h5 style='text-align: center; color:#034ea2;'>VMs Gesamt: { df_vInfo_filtered['MOID'].shape[0] }</h5>", unsafe_allow_html=True)

            st.write('---')
            
            column_vm_1, column_vm_2, column_vm_3 = st.columns(3)            

            with column_vm_1:        
                st.markdown(f"<h6 style='text-align: center; color:#000000;'>Top 10 VMs: vCPU (On)</h6>", unsafe_allow_html=True)                
                top_vms_vCPU = custom_functions.generate_top10_vCPU_VMs_df(df_vCPU_filtered)
                st.table(top_vms_vCPU)
            with column_vm_2:
                st.markdown(f"<h6 style='text-align: center; color:#000000;'>Top 10 VMs: vMemory (On)</h6>", unsafe_allow_html=True)
                top_vms_vMemory = custom_functions.generate_top10_vMemory_VMs_df(df_vMemory_filtered)
                st.table(top_vms_vMemory)
            with column_vm_3:
                st.markdown(f"<h6 style='text-align: center; color:#000000;'>Top 10 VMs: vStorage consumed</h6>", unsafe_allow_html=True)
                top_vms_vStorage_consumed = custom_functions.generate_top10_vStorage_consumed_VMs_df(df_vmList_filtered)
                st.table(top_vms_vStorage_consumed)

        guest_os_expander = st.expander(label='VM Gastbetriebssystem Details')
        with guest_os_expander:
            guest_os_df = custom_functions.generate_guest_os_df(df_vmList_filtered)
            st.table(guest_os_df)
            st.write('Ein Auslesen der Gastbetriebssysteme setzt u.A. vorraus dass die passenden Guest Tools in den VMs installiert sind und diese eingeschaltet sind/waren. Dies ist i.d.R. nicht überall der Fall daher zeigt die obige Tabelle nur die Gastbetriebssysteme von den VMs bei welchen solch ein Auslesen möglich war.')


        vCPU_expander = st.expander(label='vCPU Details')
        with vCPU_expander:
            column_vCPU_overview, column_vCPU_performance_based = st.columns([1,2])
            with column_vCPU_overview:
                st.markdown(f"<h5 style='text-align: center; color:#000000; background-color: #F5F5F5;'>Generelle vCPU Auswertung</h5>", unsafe_allow_html=True)

            with column_vCPU_performance_based:
                st.markdown(f"<h5 style='text-align: center; color:#000000; background-color: #F5F5F5;'>Nutzungs-basierte vCPU Auswertung (On)</h5>", unsafe_allow_html=True)

            vCPU_provisioned_df, vCPU_overview_df = custom_functions.generate_vCPU_overview_df(df_vCPU_filtered,df_vHosts_filtered)
            
            column_vCPU_overview_table, column_vCPU_performance_based_table, column_vCPU_performance_based_chart = st.columns([2,1.5,2.5])                            

            with column_vCPU_overview_table:
                st.table(vCPU_provisioned_df)
                
            with column_vCPU_performance_based_table:
                st.table(vCPU_overview_df)

            with column_vCPU_performance_based_chart:
                bar_chart_vCPU, vCPU_bar_chart_config = custom_functions.generate_bar_charts(vCPU_overview_df.data, "vCPUs", 350)
                st.plotly_chart(bar_chart_vCPU,use_container_width=True, config=vCPU_bar_chart_config)                

            st.write('Der Nutanix Collector kann neben den zugewiesenen vCPU Ressourcen an die VMs ebenfalls die Performance Werte der letzten 7 Tage in 30 Minuten Intervallen aus vCenter/Prism auslesen und bietet anhand dessen eine Möglichkeit für Rückschlüsse auf tatsächlich verwendete / benötigte vCPU Ressourcen. Bei den hier rechts gezeigten Nutzungs-basierten Auswertung wird die jeweils prozentuale Auslastung pro angeschalteter VM mit den zugewiesenen vCPU Werten multipliziert und mit zusätzlich 20% Puffer versehen. **Da vCPU überprovisioniert werden kann, bietet es sich an die tatsächlich benötigten vCPU Werte zu verwenden (95th Percentile empfohlen).**')

        vRAM_expander = st.expander(label='vRAM Details')
        with vRAM_expander:
            column_vRAM_overview, column_vRAM_performance_based = st.columns([1,2])
            with column_vRAM_overview:
                st.markdown(f"<h5 style='text-align: center; color:#000000; background-color: #F5F5F5;'>Generelle vMemory Auswertung</h5>", unsafe_allow_html=True)

            with column_vRAM_performance_based:
                st.markdown(f"<h5 style='text-align: center; color:#000000; background-color: #F5F5F5;'>Nutzungs-basierte vMemory Auswertung (On)</h5>", unsafe_allow_html=True)

            vRAM_provisioned_df, vMemory_overview_df = custom_functions.generate_vRAM_overview_df(df_vMemory_filtered)
            
            column_vRAM_overview_table, column_vRAM_performance_based_table, column_vRAM_performance_based_chart = st.columns([2,1.5,2.5])                            

            with column_vRAM_overview_table:
                st.table(vRAM_provisioned_df)
                
            with column_vRAM_performance_based_table:
                st.table(vMemory_overview_df)

            with column_vRAM_performance_based_chart:
                bar_chart_vMemory, vMemory_bar_chart_config = custom_functions.generate_bar_charts(vMemory_overview_df.data, "GiB", 250)
                st.plotly_chart(bar_chart_vMemory,use_container_width=True, config=vMemory_bar_chart_config)                

            st.write('Der Nutanix Collector kann neben den zugewiesenen vMemory Ressourcen an die VMs ebenfalls die Performance Werte der letzten 7 Tage in 30 Minuten Intervallen aus vCenter/Prism auslesen und bietet anhand dessen eine Möglichkeit für Rückschlüsse auf tatsächlich verwendete / benötigte vMemory Ressourcen. Bei den hier rechts gezeigten Nutzungs-basierten Auswertung wird die jeweils prozentuale Auslastung pro angeschalteter VM mit den zugewiesenen vMemory Werten multipliziert und mit zusätzlich 20% Puffer versehen. **Da vMemory nicht überprovisioniert werden sollte, sollte beim Sizing lediglich die konfigurierten/provisioned Werte verwendet werden.** Die tatsächliche Auslastung kann aber Rückschlüsse auf ein potenzielles Optimierungspotenzial und und damit verbundenen Kosteneinsparungen aufzeigen.')

        vStorage_expander = st.expander(label='vStorage Details')
        with vStorage_expander:
            st.write('Hier vStorage Auswertung einbauen, ggf mit Diagramm')
        
    with sizing_section: 

        st.markdown("---")    
            
        st.markdown('### Sizing-Eckdaten-Berechnung')

        with st.form('filter_form'):

            
            vCluster_selected = st.multiselect(
                "vCluster selektieren:",
                options=sorted(df_vInfo["Cluster Name"].unique()),
                default=sorted(df_vInfo["Cluster Name"].unique())
            )


            form_row_2_1, form_row_2_2, form_row_2_3 = st.columns(3)
            with form_row_2_1:
                st.markdown("<h4 style='text-align: center; color:#034ea2;'>vCPU Sizing:</h4>", unsafe_allow_html=True)
                vCPU_powerstate_selected = st.multiselect(
                    "vCPU VM Power-Status selektieren:",
                    options=sorted(df_vInfo["Power State"].unique()),
                    default='poweredOn'
                )
                vCPU_selected = st.selectbox('Sizing vCPU Werte:', ('95th Percentile','Peak','Provisioned','Average','Median'))
                st.markdown("<p style='text-align: center;'><i>95th Percentile empfohlen.</i></p>", unsafe_allow_html=True)
                vCPU_growth_selected = st.slider('Wieviel % vCPU Wachstum?', 0, 100, 10)
                
            with form_row_2_2:
                st.markdown("<h4 style='text-align: center; color:#034ea2;'>vMemory Sizing:</h4>", unsafe_allow_html=True)
                vMemory_powerstate_selected = st.multiselect(
                    "vMemory VM Power-Status selektieren:",
                    options=sorted(df_vInfo["Power State"].unique()),
                    default='poweredOn'
                )
                vMemory_selected = st.selectbox('Sizing vMemory Werte:', ('Provisioned','95th Percentile','Peak','Average','Median'))
                st.markdown("<p style='text-align: center;'><i>Provisioned empfohlen.</i></p>", unsafe_allow_html=True)
                vMemory_growth_selected = st.slider('Wieviel % vMemory Wachstum?', 0, 100, 30)
            with form_row_2_3:
                st.markdown("<h4 style='text-align: center; color:#034ea2;'>vStorage Sizing:</h4>", unsafe_allow_html=True)
                vStorage_powerstate_selected = st.multiselect(
                    "vStorage VM Power-Status selektieren:",
                    options=sorted(df_vInfo["Power State"].unique()),
                    default=sorted(df_vInfo["Power State"].unique())
                )
                vStorage_selected = st.selectbox('Sizing vStorage Werte:', ('in Use','Provisioned'))
                st.markdown("<p style='text-align: center;'><i>In Use (nach Rücksprache) empfohlen.</i></p>", unsafe_allow_html=True)
                vStorage_growth_selected = st.slider('Wieviel % Storage Wachstum?', 0, 100, 20)

            filter_form_submitted = st.form_submit_button(label = 'Auswertung starten ✔️')   
        