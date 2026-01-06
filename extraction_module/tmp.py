import networkx as nx
import plotly.graph_objs as go
import nibabel as nib
import os

class Visualisation:
    def __init__(
            self,
            graph: nx.Graph = None,
            sphere_radius: float = 100,
            title: str = "Graph",
            window_width: int = 1000,
            window_height: int = 1000,
            mesh_opacity: float = None,
            camera: dict = None,
            lighting_effects: dict = None,
            lightposition: dict = None,
            colorscale: str = None
    ):
        """
        Object to visualise a graph.
        :param graph: graph paremeter
        :param sphere_radius: sphere radius parameter
        :param title: title of the graph visualisation
        :param window_width: html window width
        :param window_height: html window height
        """
        self.graph = graph
        self.title = title
        self.window_width = window_width,
        self.window_height = window_height,
        self.radius = sphere_radius
        self.fig = go.Figure()
        self.points = None
        self.labels = None
        if mesh_opacity is None:
            self.mesh_opacity = 1
        else:
            self.mesh_opacity = mesh_opacity
        self.camera = dict(
            eye=dict(x=2, y=0, z=0),  # Camera position from lateral side
            center=dict(x=0, y=0, z=0),  # Looking at center
            up=dict(x=0, y=0, z=1)  # Up vector points in positive z direction
        )
        self.lighting_effects = dict(ambient=0.4, diffuse=0.5, roughness=0.9, specular=0.6, fresnel=0.2)
        self.lightposition = dict(
            x=-10, y=10, z=10
        )
        self.colorscale = 'jet'
        self.all_color = [
            'Red', 'Blue', 'Green', 'Yellow', 'Orange', 'Purple', 'Pink', 'Brown', 'Black', 'White',
            'Gray', 'Violet', 'Cyan', 'Magenta', 'Lime', 'Maroon', 'Olive', 'Navy', 'Teal', 'Aqua',
            'Coral', 'Turquoise', 'Beige', 'Lavender', 'Salmon', 'Gold', 'Silver', 'aliceblue', 'Khaki',
            'Indigo', 'Plum'
        ]
        if self.graph is not None:
            self.extract_coord_label()
            self.construct_sphere()

    def save_as_html(self, path_to_save: str) -> None:
        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)
        self.fig.write_html(os.path.join(path_to_save, self.title + ".html"))

    def plot_mesh(
            self,
            mesh_path: str,
    ) -> None:
        print(mesh_path)
        mesh = nib.load(mesh_path)
        vertices = mesh.darrays[0].data.astype(float)
        faces = mesh.darrays[1].data.astype(int)
        self.fig.add_trace(go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            color='Beige',
            opacity=self.mesh_opacity,
            name="Mesh Full Opacity",
            lighting=self.lighting_effects,
            lightposition=self.lightposition,
        ))

        self.fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                camera=self.camera,
            ),
            showlegend=True,
            title=self.title
        )
    def show_fig(self):
        self.fig.show()
        self.fig.data = []


if __name__ == "__main__":
    main_path = "/envau/work/meca/data/babofet_DB/2024_new_stuff/atlas_fetal_rhesus_v2/"
    subjects = ["Fabienne"]
    sessions = ["01"]
    sides = ["left", "right"]
    suffix = ""
    for subject in subjects:
        for session in sessions:
            for side in sides:
                title = f"{subject}_ses{session}_{side}{suffix}"
                vis = Visualisation(title=title)
                vis.plot_mesh(os.path.join(main_path, f"Surf_Hemi/{subject}/{subject}_ses{session}{suffix}.{side}.white.gii"))
                vis.save_as_html(os.path.join(main_path, f"Surf_Hemi_html/{subject}"))
                vis.show_fig()
