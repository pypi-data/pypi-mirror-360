import matplotlib.pyplot as plt

def _plot_text(text, _fontsize=14) -> object:
    '''
    Plot a text in matplotlib. Useful to show some simple LaTeX codes.
    '''
    fig, ax = plt.subplots( figsize=(0.1, 0.1))
    ax.text(0, 0, f'{text}', fontsize=_fontsize)
    # Remove axis
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    # Remove boders
    ax.spines[:].set_visible(False)
    return fig, ax