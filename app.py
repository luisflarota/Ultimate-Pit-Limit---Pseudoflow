import re
from statistics import mode

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import back

global colors
colors = ["#F9E79F", '#82E0AA', '#922B21', '#08056B', '33FFF4', 'FC33FF', 'FF8333', '070300']
#ranges = [[-1000000,0], [0,30000], [30000,1000000]]
rang_def = [[0,0.3], [0.3,0.6], [0.6,1], [1,10]]
def main():
    st.set_option('deprecation.showfileUploaderEncoding', False)
    st.image('logo.jpg')

    st.sidebar.write('Do you have a block model file?')
    say_yes = st.sidebar.checkbox('Yes')
    say_no = st.sidebar.checkbox('No')
    if say_yes and say_no:
        st.sidebar.success('Please choose only one option')
    elif say_no:
        #if st.sidebar.radio('',['Choose default file']):
        st.sidebar.success('Loading default file')
        load_file('block_model_test.csv')
    elif say_yes:
        file_= st.sidebar.file_uploader('*Upload or drop the file:')
        if file_:
            load_file(file_)

def load_file(file_model):
    if file_model:
        separator = st.sidebar.radio('*csv file delimiter:', (',', ';'))
        if separator is not None:
            #We are calling the block model here:
            model = back.blockmodel(pd.read_csv(file_model, skipinitialspace= True, sep = separator))    
            x = st.sidebar.selectbox('X coordinate:', model.columns())
            y = st.sidebar.selectbox('Y coordinate:', model.columns())
            z = st.sidebar.selectbox('Z coordinate:', model.columns())
            grade = st.sidebar.selectbox('Main Grade:', model.columns(), help='Please, units of grades must be in percentage')
            density = st.sidebar.selectbox('Density:', model.columns())
            
            #Load archive:
            if st.sidebar.checkbox('Load'):
                try:
                    analize(model, x,y,z, grade, density)
                except:
                    st.info('Check your data carefully, i.e., units, coordinates, etc.')

        

def analize(model,x,y,z, grade,density):
    st.success('Based on your file:')
    model.summary(x,y,z, grade, density)()
    st.markdown('I got:')
    st.write('{} blocks in X'.format(model.xlong))
    st.write('{} blocks in Y'.format(model.ylong))
    st.write('{} blocks in Z'.format(model.zlong))
    total_block_times = model.long
    if total_block_times != model.summary_2():
        st.warning('Message: You need to have {:,.0f} blocks. However, you got {:,.0f} blocks'.format(total_block_times, model.bmodel.shape[0]))
        if st.checkbox('Check outliers in the block model:'):
            #Cleanning gets [outliers]
            outliers = model.cleanning()
            st.write('I am taking out the following blocks:')
            st.dataframe(outliers)
            print(outliers)
            #Asking one more time, if it wants to re-analyze de file
            analyze_again = st.radio('Analyze again?:', ['No', 'Yes'])
            if analyze_again == 'Yes':
                model = back.blockmodel(model.bmodel)
                analize(model, x,y,z, grade, density)
                
    #If number of blocks = to unique values on x,y,z then:
    elif total_block_times == model.summary_2():
        st.success('Awesome! Now, # blocks = # rows')
        #Calling visualizer that needs more development (blocks sizing)
        if st.checkbox('3D Block model visualization'):
            visualize_model(model, x,y,z, grade, density)
        if st.checkbox('Get Grade-Tonnage Distribution'):
            if type(grade) == str:
                grade = [grade]
            #Choosing main grade for the exercise
            select_mgrade = st.selectbox('Select your main grade:', grade)
            st.plotly_chart(call_grade_tonnage(model, select_mgrade, density))   
            if st.checkbox('Get the Ultimate Pit Limit'):
                m_c = st.number_input('Mining Cost (USD/Ton.)', value = 4)  #(USD/ Ton.)
                opt_increm = st.selectbox('Incremental Cost?', ['Yes', 'No'])
                if opt_increm == 'Yes':    
                    i_c  = st.text_input('Incremental Cost (USD/ton.)', help='Does the mining cost increment while going deep? This is added to the mining cost while going 1 meter deep.',value = 0.01) #(USD/ Ton./ meter deep)
                else:
                    i_c = 0
                p_c  = st.number_input('Processing Cost (USD/ton.)', value = 9)  #(USD/ Ton.)
                t_c = st.number_input('Treatment Cost (USD/lb.)', value = 0.1)  #(USD/ lb.)
                m_p = st.number_input('Metal Price (USD/lb.)', value = 3.1)  #(USD/ lb.)
                m_r = st.number_input('Metal Recovery (<1)', value = 0.9) #
                prec = st.selectbox('Select block precedences:', ['1-5 pattern','1-9 pattern'], key= 'the_prec', help='45 degrees if 105 pattern, 40 degrees otherwise.')

                if st.button('Solve the Ultimate Pit Limit problem'):
                    model_solve = model.upl(x,y,z, select_mgrade, density, m_c, float(i_c), p_c, t_c, m_p, m_r, prec)
                    return st.plotly_chart(visualize_upl(model_solve, x,y,z, select_mgrade, rang_def, colors),use_container_width=True)


def visualize_model(model, x,y,z, grade, density):
    st.warning('Select the portion of the block model you want to see:')
    x_slider =  st.slider('Range for X coordinates:', model.minx, model.maxx, (model.minx, model.minx + 5*model.modex), model.modex)
    y_slider =  st.slider('Range for Y coordinates:', model.miny, model.maxy, (model.miny, model.miny + 5*model.modey), model.modey)
    z_slider =  st.slider('Range for Z coordinates:', model.minz, model.maxz, (model.minz, model.minz + 5*model.modez), model.modez)
    st.warning('How do you want to split grades?:')
    text_1 = 'Select ranges with only 1 decimal - i.e., 0.1, 0.2, 0.3, 2.0 (max. 8 numbers)'
    st.write(text_1)
    p_compile = re.compile(r'\d+\.\d+')
    min_grade, max_grade = min_max(model.bmodel, x,y,z, x_slider, y_slider, z_slider, grade)
    ranges = st.text_input('Minimun grade is: {}, and maximum one is: {}'.format(min_grade, max_grade))
    # Compile a pattern to capture float values
    # Convert strings to float
    # Asking to visualize
    ask_visualize = st.radio('Visualize:', ['No', 'Yes'])
    if ask_visualize == 'Yes':
        floats = [float(i) for i in p_compile.findall(ranges)]
        floats = list_maker(floats)
        st.plotly_chart(visualize(model.bmodel, x,y,z, x_slider, y_slider, z_slider, grade, floats, density, colors))

# Min_max to plot grade distribution
def min_max(model, x,y,z, x_slider, y_slider, z_slider, grade):
    for_plot = model.loc[((model.loc[:, x]>= x_slider[0]) & (model.loc[:,x] <= x_slider[1])) & \
        ((model.loc[:,y]>= y_slider[0]) & (model.loc[:,y] <= y_slider[1]))&\
            ((model.loc[:,z]>= z_slider[0]) & (model.loc[:,z] <= z_slider[1]))]
    min_ = round(min(for_plot.loc[:, grade]),3)
    max_ = round(max(for_plot.loc[:, grade]),3)        
    return min_,max_
#Visualizing the whole, remember to use . as decimal separator
def visualize(model, x,y,z, x_slider, y_slider, z_slider, grade, floats, density, colors):
    i = 0
    for_plot = model.loc[((model.loc[:, x]>= x_slider[0]) & (model.loc[:,x] <= x_slider[1])) & \
        ((model.loc[:,y]>= y_slider[0]) & (model.loc[:,y] <= y_slider[1]))&\
            ((model.loc[:,z]>= z_slider[0]) & (model.loc[:,z] <= z_slider[1]))]
    fig = go.Figure()
    #set ranges with colors:
    for value in floats:
        before = value[0]
        after = value[1]
        data_plot = for_plot.loc[(for_plot.loc[:,grade]>= before) & (for_plot.loc[:,grade]< after)]
        data_plot.loc[:, grade] =data_plot.loc[:, grade].round(3)
        data_plot.loc[:, 'g'] = '{}: '.format(grade) + data_plot.loc[:, grade].astype(str)
        #naming the plot on the legend
        name_legend = str(before) + " <=" + grade +"< " +str(after)
        fig.add_trace(go.Scatter3d(x = data_plot.loc[:, x], y = data_plot.loc[:,y], z = data_plot.loc[:,z], text= data_plot.loc[:,'g'],mode = 'markers'\
                                , name = name_legend, marker = dict(color = colors[i], symbol = 'square', size = 4), showlegend = True))
        i+=1
    title = '<b>Grade Distribution in the Block Model </b>'

    fig.update_layout(margin = dict(r=100, t=25, b=40, l=100), title = title)
    
    return fig

#Grade-tonnage curve
def call_grade_tonnage(model, grade, density):
    
    volume = model.modex * model.modey * model.modez
    modelo = model.bmodel
    modelo.loc[:,'ton'] = volume * modelo.loc[:,density]
    modelo.loc[:,'ton_g'] = modelo.loc[:,'ton']  * modelo.loc[:,grade]/100

    cutoff_grade = list(np.arange(0,2, 0.05))
    ton_a_cutoff = []
    ton_cutfine = []
    for i in cutoff_grade:
        x = modelo[modelo.loc[:, grade]>=i]['ton'].sum()/1000000000
        y = modelo[modelo.loc[:, grade]>=i]['ton_g'].sum()/1000000000
        ton_a_cutoff.append(x)
        ton_cutfine.append(y)
    grade_ton_dist = pd.DataFrame({'Cutoff_grade': cutoff_grade, 'GTon_a_cutoff': ton_a_cutoff, 'GTon_cutfine' : ton_cutfine})
    grade_ton_dist['Cut_Grade'] = grade_ton_dist['GTon_cutfine']*100/grade_ton_dist['GTon_a_cutoff']
    title = '<b>Grade - Tonnage Distribution for {} grade</b>'.format(grade)
    #8 We can plot it .. so now it may be familiar to you (PD: Forgot to grab some packages)
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x = grade_ton_dist['Cutoff_grade'], y = grade_ton_dist['GTon_a_cutoff'], name = 'Tonnage (Gtons.)  vs. Cut-off grade (%)'), secondary_y = False) 
    fig1.add_trace(go.Scatter(x = grade_ton_dist['Cutoff_grade'], y = grade_ton_dist['Cut_Grade'], name = 'Avg. grade (%) vs Cut-off grade (%)'), secondary_y = True)
    fig1.update_xaxes(title_text = "<b>Cut-off grade (%)<b>")
    fig1.update_yaxes(title_text="<b>Tonnage (GT.)</b>", secondary_y =False)
    fig1.update_yaxes(title_text="<b>Avg. grade (%)</b>", secondary_y =True)
    fig1.update_layout(title = title)
    model.bmodel = modelo
    return fig1

def list_maker(lista):
    list_ranges = []
    for i in range(len(lista)):
        if i == len(lista)-1:
            break
        else:
            bef = lista[i]
            after = lista[i+1]
            list_ranges.append([bef, after])
    return list_ranges


def visualize_upl(model, xcol, ycol, zcol, grade, ranges, colors):
    i = 0
    fig = make_subplots(rows = 9, cols = 2, specs = [[{'type': 'scatter3d', 'rowspan':6, 'colspan':2}, None],
                                                [None, None],
                                                [None, None],
                                                [None, None],
                                                [None, None],
                                                [None, None],
                                                [{'type': 'bar', 'rowspan':3,'colspan':2}, None],
                                                [None, None],
                                                [None, None]])
    #set ranges with colors:
    for value in ranges:
        before = value[0]
        after = value[1]
        data_plot = model[(model.loc[:,grade]>= before) & (model.loc[:,grade]< after)]
        #This one is for the histogram
        freq = data_plot.shape[0]
        data_plot.loc[:,grade] =data_plot.loc[:,grade].round(3)
        data_plot.loc[:,'g'] = '{}: '.format(grade) + data_plot.loc[:,grade].astype(str)
        #naming the plot on the legend
        name_legend = str(before) + " <=" + grade +"< " +str(after)
        fig.add_trace(go.Scatter3d(x = data_plot.loc[:,xcol], y = data_plot.loc[:,ycol], z = data_plot.loc[:,zcol], text= data_plot.loc[:,'g'],mode = 'markers'\
                                , name = name_legend, marker = dict(color = colors[i], symbol = 'square', size = 4), showlegend = True))
        fig.add_trace(go.Bar(x = [name_legend], y = [freq], marker=dict(color = colors[i]), showlegend = False, name = '', text = [freq], textposition = 'auto'), row = 7, col=1)
        i+=1

    #Include the precedence in the title!!!!!
    fig.update_layout(title = '<b>Ultimate Pit Limit</b>' + '<br>'+ \
                  '<i>Undiscounted value ot the pit: </i>'+ '<b>USD {0:,.2f}</b>'.format(model.iloc[:,4].sum()),
                 annotations = [{'font': {'size':14},'text': '<b>Histogram for grades within the ultimate pit limit</b>', 'x': 0.2, 'showarrow': False, 'y': 0.30, 
                                    'xanchor': 'center', 'xref': 'paper', 'yanchor':'bottom', 'yref': 'paper'}],
                 yaxis2 = {'anchor': 'x2', 'domain': [0.0, 0.5]},
                 legend = dict(x = 1.0, y = 1.0, font = dict(size = 13)))

    fig.update_yaxes(title_text = 'Frequency', row = 9, col = 1)
    fig.update_xaxes(title_text = 'Grade Ranges', row = 9, col = 1)
    return fig
if __name__ ==  '__main__':
    main()
