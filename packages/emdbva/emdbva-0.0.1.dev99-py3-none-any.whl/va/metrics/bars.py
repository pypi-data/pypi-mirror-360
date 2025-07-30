import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def load_score(input_file, new_entry, score_type):
    """
    Load score into dataframe
    """

    type_dict = {'id': str, 'resolution': float, 'name': str, score_type: float}
    df_nonew = pd.read_csv(input_file, dtype=type_dict)
    new_entry_df = pd.DataFrame([new_entry])
    df = pd.concat([df_nonew, new_entry_df], ignore_index=True)
    # df_without_nan = df[~df.isnull().any(axis=1)].sort_values(by=score_type).reset_index()
    df_without_nan = df[~df[score_type].isnull()].sort_values(by=score_type).reset_index()
    subsets = ['id', 'resolution', 'name', score_type]
    df_without_nan = df_without_nan.drop_duplicates(subsets)

    return df_without_nan


def get_score(df, input_value, score_type):
    """
    Given the dataframe, return a tuple one contain min and max of the score and
    the other contains the number of items smaller than the input value and number
    of items larger than the input value
    """

    qmin = None
    qmax = None
    small = None
    large = None
    if not df.empty:
        qmin = df[score_type].min()
        qmax = df[score_type].max()
        large = df[df[score_type] > input_value].shape[0]
        small = df[df[score_type] <= input_value].shape[0]

    return (qmin, qmax), (small, large)


def match_to_newscale(original_scale, target_scale, original_value):
    """
    Scale the original_value based in the original_scale to target_scale
    """

    original_min = original_scale[0]
    original_max = original_scale[1]

    target_min = target_scale[0]
    target_max = target_scale[1]

    target_value = ((original_value - original_min) / (original_max - original_min)) * (
                target_max - target_min) + target_min

    return target_value


def get_nearest_onethousand(new_entry, df, n, score_type):
    """
    Sort the score based on resolution and then return the nearest 1000 center at the
    new_entry
    """

    # Find the index of the nearest row to the target value
    cdf = df.sort_values(by='resolution').reset_index()
    # nearest_index = (cdf['qscore'] - new_entry['qscore']).abs().idxmin()
    # nearest_index = cdf[cdf['id'] == new_entry['id']].index.to_list()[0]
    # As the new entry added into the df, use all the 4 columns to identify the row index
    mask = (cdf['id'] == new_entry['id']) & (cdf['resolution'] == new_entry['resolution']) & (
                cdf['name'] == new_entry['name']) & (cdf[score_type] == new_entry[score_type])
    nearest_index = cdf[mask].index[0]

    # Get the 1000 rows centered around the nearest index
    start = max(nearest_index - n, 0)
    end = min(nearest_index + n, len(df))
    df_nearest = cdf.iloc[start:end + 1]

    return df_nearest


def get_resolution_range(new_entry, df, score_type, resbin=0.5):
    """
    Sort the df based on the resolution and then find the nearest +1-1 resolution df
    """

    if new_entry['resolution']:
        # Find the index of the nearest row to the target value
        cdf = df.sort_values(by='resolution').reset_index()
        # nearest_index = (cdf['qscore'] - new_entry['qscore']).abs().idxmin()
        # nearest_index = cdf[cdf['id'] == new_entry['id']].index.to_list()[0]
        # As the new entry added into the df, use all the 4 columns to identify the row index
        mask = (cdf['id'] == new_entry['id']) & (cdf['resolution'] == new_entry['resolution']) & (
                    cdf['name'] == new_entry['name']) & (cdf[score_type] == new_entry[score_type])
        nearest_index = cdf[mask].index

        # Get the 1000 rows centered around the nearest index
        start = float(new_entry['resolution']) - resbin if float(new_entry['resolution']) >= resbin else 0.
        end = float(new_entry['resolution']) + resbin
        df_resbin = cdf[(cdf['resolution'] >= start) & (cdf['resolution'] <= end)]

        return df_resbin
    else:
        return None


def plot_bar_mat(a, b, qmin, qmax, qscore, work_dir, plot_name, score_type):
    """
    This function here using matplotlib to produce the Q-score bar image
    """

    a = a*1.5 if a else None
    b = b*1.5 if b else None
    a = a/200 if a else None
    b = b/200 if b else None
    # Create a color scale from 0 to 1
    color_scale = np.linspace(0, 1, 199)

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 2), dpi=300)
    plt.rcParams['font.family'] = 'Times New Roman'

    # Reverse the color map
    cmap = plt.get_cmap("bwr")
    reversed_cmap = cmap.reversed()
    # Plot the color scale with a thinner aspect ratio
    ax.imshow([color_scale], cmap=reversed_cmap, aspect=0.05, extent=[0, 1.5, 0, 1])

    # Calculate the height and half-width of the diamonds
    diamond_height = 0.65
    diamond_half_width = 0.01

    # Add diamond-shaped marker for 'a'
    if a != b:
        ax.fill(
            [a - diamond_half_width, a, a + diamond_half_width, a],
            [0.5, 0.5 + diamond_height, 0.5, 0.5 - diamond_height],
            color='Black', edgecolor='black'
        )

        # Add diamond-shaped marker for 'b'
        ax.fill(
            [b - diamond_half_width, b, b + diamond_half_width, b],
            [0.5, 0.5 + diamond_height, 0.5, 0.5 - diamond_height],
            facecolor='none', edgecolor='black'
        )
    else:
        # ax.fill(
        #     [b - diamond_half_width, b, b + diamond_half_width, b],
        #     [0.5, 0.5 + diamond_height, 0.5, 0.5 - diamond_height],
        #     facecolor='yellow', edgecolor='black'
        # )
        top = np.array([[b-diamond_half_width, 0.5], [b, 0.5 + diamond_height], [b + diamond_half_width, 0.5], [b, 0.5]])
        bottom = np.array([[b-diamond_half_width, 0.5], [b, 0.5], [b + diamond_half_width, 0.5], [b, 0.5 - diamond_height]])
        top_patch = patches.Polygon(top, closed=True, facecolor='black', edgecolor='black')
        bottom_patch = patches.Polygon(bottom, closed=True, facecolor='none', edgecolor='black')
        ax.add_patch(top_patch)
        ax.add_patch(bottom_patch)

    # add four values as annotationso
    worse = r'$\it{Worse}$'
    better = r'$\it{Better}$'
    ax.annotate(worse, (0, -0.9), color='black', ha='left', fontsize=10, )
    ax.annotate(better, (1.5, -0.9), color='black', ha='right', fontsize=10)
    ax.annotate(f'{qscore:.3f}', (1.58, 0.2), color='black', ha='center', fontsize=12)

    if score_type == 'ccc':
        ax.annotate('CCC', (-0.11, 0.2), color='black', ha='center', fontsize=12)
    elif score_type == 'ai':
        ax.annotate('Atom inclusion', (-0.20, 0.2), color='black', ha='center', fontsize=12)
    elif score_type == 'smco':
        ax.annotate('SMOC', (-0.11, 0.2), color='black', ha='center', fontsize=12)
    elif score_type == 'qscore':
        ax.annotate('Q-score', (-0.11, 0.2), color='black', ha='center', fontsize=12)
    else:
        ax.annotate(score_type.upper(), (-0.11, 0.2), color='black', ha='center', fontsize=12)

    ax.annotate('Metric', (-0.11, 1.7), color='black', ha='center', fontsize=14)
    ax.annotate('Percentile Ranks', (0.75, 1.7), color='black', ha='center', fontsize=14)
    title = plot_name[:-8]
    ax.annotate(title, (0.75, 3.3), color='black', ha='center', fontsize=14, fontweight='bold')
    ax.annotate('Value', (1.58, 1.7), color='black', ha='center', fontsize=14)
    # if a >= b:
    #    ax.annotate(f'{a*100/1.5:.2f}%', (a, 1.4), color='black', ha='left', fontsize=10)
    #    #ax.annotate(f'{b:.2f}', (b, -0.8), color='black', ha='center', fontsize=10)
    #    #ax.annotate(f'{a*100:.2f}%', (a, 1.4), color='black', ha='center', fontsize=10)
    #    ax.annotate(f'{b*100/1.5:.2f}%', (b, 1.4), color='black', ha='right', fontsize=10)
    # else:
    #    ax.annotate(f'{a*100/1.5:.2f}%', (a, 1.4), color='black', ha='right', fontsize=10)
    #    #ax.annotate(f'{b:.2f}', (b, -0.8), color='black', ha='center', fontsize=10)
    #    #ax.annotate(f'{a*100:.2f}%', (a, 1.4), color='black', ha='center', fontsize=10)
    #    ax.annotate(f'{b*100/1.5:.2f}%', (b, 1.4), color='black', ha='left', fontsize=10)

    # Customize the plot
    ax.set_xlim(-0.4, 1.7)
    # ax.set_ylim(-4.3, 1.8)
    # to fit the EMD id
    ax.set_ylim(-4.3, 3.6)
    ax.set_yticks([])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Remove the left and bottom axis lines (optional)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    if a != b:
        # Add diamond-shaped marker for legend
        wa = 0.01
        ha = -2.0
        ax.fill(
            [wa - diamond_half_width, wa, wa + diamond_half_width, wa],
            [ha, ha + diamond_height, ha, ha - diamond_height],
            color='black', edgecolor='black'
        )
        ax.annotate(f'Percentile relative to all EM structures', (wa + 3 * diamond_half_width, ha - 0.25),
                    color='black', ha='left', fontsize=11)

        bwa = 0.01
        bha = -3.6
        ax.fill(
            [bwa - diamond_half_width, bwa, bwa + diamond_half_width, bwa],
            [bha, bha + diamond_height, bha, bha - diamond_height],
            facecolor='none', edgecolor='black'
        )
        ax.annotate('Percentile relative to EM structures of $\pm$1 $\mathrm{\AA}$ (resolution)',
                    (bwa + 3 * diamond_half_width, bha - 0.25), color='black', ha='left', fontsize=11)
        # ax.annotate(f'Percentile relative to EM structures of nearest 1000 (resolution)', (bwa + 3*diamond_half_width, bha-0.25), color='black', ha='left', fontsize=11)
    else:
        # Add diamond-shaped marker for legend
        wa = 0.01
        ha = -2.0
        ax.fill(
            [wa - diamond_half_width, wa, wa + diamond_half_width, wa],
            [ha, ha + diamond_height, ha, ha - diamond_height],
            color='black', edgecolor='black'
        )
        ax.annotate('Percentile relative to all EM structures (overlapped)', (wa + 3 * diamond_half_width, ha - 0.25),
                    color='black', ha='left', fontsize=11)
        # ax.annotate('Percentile relative to all EM structures (overlapped)', (wa + 3*diamond_half_width, ha-0.25), color='black', ha='left', fontsize=11)

        bwa = 0.01
        bha = -3.6
        ax.fill(
            [bwa - diamond_half_width, bwa, bwa + diamond_half_width, bwa],
            [bha, bha + diamond_height, bha, bha - diamond_height],
            facecolor='none', edgecolor='black'
        )
        ax.annotate('Percentile relative to EM structures of $\pm$1 $\mathrm{\AA}$ (resolution)',
                    (bwa + 3 * diamond_half_width, bha - 0.25), color='black', ha='left', fontsize=11)
        # ax.annotate(f'Percentile relative to EM structures of nearest 1000 (resolution)', (bwa + 3*diamond_half_width, bha-0.25), color='black', ha='left', fontsize=11)

    ax.tick_params(axis='both', which='both', length=0)
    plt.gca().set_xticklabels([])
    # Show the plot
    plot_name = '{}{}'.format(work_dir, plot_name)
    plt.savefig(plot_name)
    plt.close()


def bar(new_entry_dict, score_type, work_dir, score_dir, plot_name):
    input_file = '{}/qscores.csv'.format(score_dir)
    print(input_file)
    # new_entry_dict = {'id': '8117', 'resolution': 2.95, 'name': '5irx.cif', 'qscore': 0.521}
    qmin = None
    qmax = None
    df = load_score(input_file, new_entry_dict, score_type)
    if score_type and new_entry_dict[score_type]:
        (qmin, qmax), original_value = get_score(df, new_entry_dict[score_type], score_type)
        target_value = int(match_to_newscale((0, sum(original_value)), (0, 199), original_value[0]))
        to_whole = round(target_value/200., 3)
        to_whole_real = round((float(original_value[0]) / float(sum(original_value))), 3)
        to_whole_counts = sum(original_value)
    else:
        to_whole = None
        to_whole_real = None
        to_whole_counts = None

    #df1000 = get_nearest_onethousand(new_entry_dict, df, 500, score_type)
    if new_entry_dict['resolution']:
        df1000 = get_resolution_range(new_entry_dict, df, score_type)
        (sqmin, sqmax), ovalue = get_score(df1000, new_entry_dict[score_type], score_type)
        target_value_two = int(match_to_newscale((0, sum(ovalue)), (0, 199), ovalue[0]))
        to_two = round(target_value_two/200., 3)
        to_two_real = round((float(ovalue[0]) / float(sum(ovalue))), 3)
        to_two_counts = sum(ovalue)
    else:
        to_two = None
        to_two_real = None
        to_two_counts = None

    if to_whole and to_two:
        plot_bar_mat(target_value, target_value_two, qmin, qmax, new_entry_dict[score_type], work_dir, plot_name, score_type)
    print(to_whole_real, to_two_real)

    return ((to_whole_real, to_whole_counts), (to_two_real, to_two_counts))
