# include flake8, black

import argparse
import os

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
from PIL import Image


def plotscatter(dim, clusters, centroids, ftitle, iter=None):
    if iter is not None:
        ftitle = ftitle + ", iter = {}".format(iter)
    cmap = plt.get_cmap("tab10")

    # plot clusters and centroids
    if dim == 2:
        fig = plt.figure()
        ax = fig.add_subplot(
            111,
            title=ftitle,
            xlabel="X",
            ylabel="Y",
        )
        for i, cluster in enumerate(clusters):
            cluster = np.array(cluster)
            plt.scatter(
                cluster[:, 0],
                cluster[:, 1],
                s=20,
                linewidths=1.3,
                marker="o",
                facecolor="None",
                edgecolors=cmap(i),
            )
        plt.scatter(
            centroids[:, 0],
            centroids[:, 1],
            s=100,
            linewidths=5,
            marker="x",
            c="k",
            label="centroid",
        )
        plt.legend()

    elif dim == 3:
        fig = plt.figure()
        ax = fig.add_subplot(
            111,
            projection="3d",
            title=ftitle,
            xlabel="X",
            ylabel="Y",
            zlabel="Z",
        )
        for i, cluster in enumerate(clusters):
            cluster = np.array(cluster)
            ax.scatter3D(
                cluster[:, 0],
                cluster[:, 1],
                cluster[:, 2],
                s=20,
                linewidths=2.0,
                marker="o",
                facecolor="None",
                edgecolors=cmap(i),
            )
        ax.scatter3D(
            centroids[:, 0],
            centroids[:, 1],
            centroids[:, 2],
            s=100,
            linewidths=5,
            marker="x",
            c="k",
            label="centroid",
        )
        plt.legend()
    return fig, ax


def k_means(data, n_clusters, centroids, max_iter=300, animation=False, ftitle=None):
    """
    k-means clustering.

    Parameters:
        data : ndarray (shape (num of data, dimension))
            Input data from csv file.
        n_clusters : int
            The number of clusters to form as well as the number of centroids to generate.
        centroids : ndarray (shape (n_clusters, dimension))
            Centroids generated by {init_random, init_lbg, init_minimax} function.
            n_clusters and the number of "centroids" element must be the same.
        max_iter : int, default=300
            Maximum number of iterations of the k-means algorithm for a single run.

    Returns:
        clusters : list
            Clusters list. The length of this list is \"n_clusters\".
        centroids : ndarray (shape (n_clusters, dimension))
            Centroids.
    """
    if n_clusters != len(centroids):
        raise ValueError(
            'n_clusters and the number of "centroids" element must be the same.'
        )

    # previous centroids
    prev_centroids = np.zeros_like(centroids)
    # number of iterations
    iter = 0
    process = []

    while np.count_nonzero(centroids - prev_centroids) and iter < max_iter:
        iter += 1
        prev_centroids = centroids.copy()

        # square of distance
        dist_sq = np.array(
            [np.sum((data - centroid) ** 2, axis=1) for centroid in centroids]
        )

        # calculate clusters and centroids
        labels = np.argmin(dist_sq, axis=0)
        clusters = [data[labels == label] for label in range(n_clusters)]
        centroids = np.array([np.mean(cluster, axis=0) for cluster in clusters])

        if animation:
            fig, _ = plotscatter(data.shape[1], clusters, centroids, ftitle, iter)
            fig.canvas.draw()
            plt.close()
            im = np.array(fig.canvas.renderer.buffer_rgba())
            img = Image.fromarray(im)
            process.append(img)
            # plt.show()
            # plt.close()

    if animation:
        print(iter)
        # print(process)
    return clusters, centroids, process


def init_random(data, n_clusters):
    """
    Select initial cluster centers for k-means clustering at random from data.

    Parameters:
        data : ndarray (shape (num of data, dimension))
            Input data from csv file.
        n_clusters : int
            The number of clusters to form as well as the number of centroids to generate.

    Returns:
        centroids : ndarray (shape (n_clusters, dimension))
            Centroids.
    """
    centroids = data[random.sample(range(len(data)), n_clusters)]
    return centroids


def init_lbg(data, n_clusters, delta=0.1):
    """
    Calculate initial cluster centers for k-means clustering by Linde-Buzo-Gray algorithm from data.

    Parameters:
        data : ndarray (shape (num of data, dimension))
            Input data from csv file.
        n_clusters : int
            The number of clusters to form as well as the number of centroids to generate.

    Returns:
        centroids : ndarray (shape (n_clusters, dimension))
            Centroids.
    """
    # rough small vector
    delta = np.full(data.shape[1], delta)

    # center of gravity
    centroids = np.array([np.mean(data, axis=0)])

    while len(centroids) < n_clusters:
        centroids = np.append(centroids - delta, centroids + delta, axis=0)
        # k-means clustering
        _, centroids, _ = k_means(data, len(centroids), centroids)

    # select centroids
    centroids = centroids[random.sample(range(len(centroids)), n_clusters)]

    return centroids


def init_minimax(data, n_clusters):
    """
    Select initial cluster centers for k-means clustering by minimax algorithm from data.

    Parameters:
        data : ndarray (shape (num of data, dimension))
            Input data from csv file.
        n_clusters : int
            The number of clusters to form as well as the number of centroids to generate.

    Returns:
        centroids : ndarray (shape (n_clusters, dimension))
            Centroids.
    """
    # select first centroid index at random
    centroids_idx = [random.choice(range(len(data)))]

    while len(centroids_idx) < n_clusters:
        # square of distance
        dist_sq = np.array(
            [np.sum((data - data[idx]) ** 2, axis=1) for idx in centroids_idx]
        )

        # find next centroid index
        max_idx = np.argmax(np.min(dist_sq, axis=0))
        centroids_idx.append(max_idx)

    # centroids index -> centroids
    centroids = data[centroids_idx]
    return centroids


def main(args):
    fname = args.fname
    n_clusters = args.n_clusters
    init = args.init

    """
    fname = "data1.csv"
    n_clusters = 5
    init = "lbg"
    """

    # get current working directory
    path = os.path.dirname(os.path.abspath(__file__))

    ftitle, fext = os.path.splitext(fname)
    save_fname = "_{0}{1}".format(init, n_clusters).join(
        [ftitle, fext.replace("csv", "png")]
    )
    fname = os.path.join(path, "data", fname)
    save_fname = os.path.join(path, "result", save_fname)

    ftitle = ftitle + "\ninit = {0}, n_clusters = {1}".format(init, n_clusters)

    # load csv file and convert to ndarray
    data = pd.read_csv(fname).values

    # k-means clustering
    centroids = eval("init_{}".format(init))(data, n_clusters)
    clusters, centroids, process = k_means(
        data, n_clusters, centroids, animation=True, ftitle=ftitle
    )
    process[0].save(
        save_fname.replace(".png", "_process.gif"),
        save_all=True,
        append_images=process[1:],
        loop=0,
        duration=300,
    )
    plt.close()
    # ani.save(save_fname.replace("png", "gif"), writer="pillow")
    # plt.show()

    fig, ax = plotscatter(data.shape[1], clusters, centroids, ftitle)
    fig.savefig(save_fname)
    plt.show()
    # plt.close()

    if data.shape[1] == 3:

        def update(i):
            """
            Move view point.

            Parameters:
                i : int
                    Number of frames.

            Returns:
                fig : matplotlib.figure.Figure
                    Figure viewed from angle designated by view_init function.
            """

            ax.view_init(elev=30.0, azim=3.6 * i)
            return fig

        # animate graph
        ani = animation.FuncAnimation(fig, update, frames=100, interval=100)
        ani.save(save_fname.replace("png", "gif"), writer="pillow")
        plt.show()


if __name__ == "__main__":
    # process args
    parser = argparse.ArgumentParser(description="k-means clustering.")
    parser.add_argument("fname", type=str, help="Load filename")
    parser.add_argument(
        "-n",
        "--n_clusters",
        type=int,
        help="The number of clusters (optional, Default = 5)",
        default=5,
    )
    parser.add_argument(
        "-i",
        "--init",
        type=str,
        help="Method to select initial centroids (optional, [random, lbg, minimax], Default = lbg)",
        default="lbg",
        choices=["random", "lbg", "minimax"],
    )
    args = parser.parse_args()
    main(args)
