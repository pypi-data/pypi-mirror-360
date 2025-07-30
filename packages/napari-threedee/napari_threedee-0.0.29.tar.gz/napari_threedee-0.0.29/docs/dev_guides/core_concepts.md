# Core concepts

`napari-threedee` provides reusable components (called **`threedee` objects**) which 
- enable custom 3D interactive functionality
- simplify the development of workflows with 3D interactivity



## How to use `napari-threedee`

`napari-threedee` is designed to be used both as a **napari plugin** and as a **library**.

When used as a **plugin**, a set of widgets provide custom 3D manipulation and 
annotation tools in napari. In this case, users need not delve into the code.

For those who want to integrate custom 3D interactivity into their application, 
`napari-threedee` can also be used as a **library**. In this case, users can
- integrate existing functionality into their applications
- develop new custom functionality more easily

## `threedee` objects
**`threedee` objects** can be split into two categories, **manipulators** and **annotators**.
They can be activated and deactivated as required.

### Manipulators
A **Manipulator** is an object in the scene which allows us to position something: a point, a plane, a layer, etc. 
It is a combination of **translators** and **rotators**. 

**Translators** have a diamond shaped handle. Clicking and dragging a **translator** will move the manipulator along the axis of the selected translator.
**Rotators** have a ball shaped handle. Clicking and dragging a **rotator** will rotate the object. 

<div style="text-align: center;"><img src="https://github.com/napari-threedee/napari-threedee/assets/76622105/3edc0809-9ba1-4e23-aae7-5e8817209240" alt="A napari-threedee manipulator"  width="50%"></div>

Manipulators can be used to modify other objects by providing callbacks which will 
be run before, during, and after an interaction with the manipulator. 

For more details see [**manipulators**](./manipulators.md)

### Annotators

An **Annotator** allows for a custom 3D data annotation mode in napari. 
This is particularly useful for orchestrating annotation behaviour which depends 
on the state of multiple layers (e.g. adding points on planes).


### Automatic widget generation

A dock widget can be generated automatically for any `threedee` object by subclassing
`QtThreeDeeWidgetBase` and providing the new `threedee` object as a model.

```python
class QtRenderPlaneManipulatorWidget(QtThreeDeeWidgetBase):
    def __init__(self,viewer: napari.Viewer, *args, **kwargs):
        super().__init__(model=RenderPlaneManipulator, viewer=viewer, *args, **kwargs)
```
