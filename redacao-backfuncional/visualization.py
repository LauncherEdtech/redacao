import plotly.graph_objects as go

def radar_chart(comp_scores):
    """
    comp_scores = [comp1, comp2, comp3, comp4, comp5]
    Retorna uma figura Plotly de Radar Chart.
    """
    categories = ['Competência 1', 'Competência 2', 'Competência 3', 'Competência 4', 'Competência 5']
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=comp_scores,
        theta=categories,
        fill='toself',
        name='Atual'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 200]
            )
        ),
        showlegend=False
    )
    return fig
