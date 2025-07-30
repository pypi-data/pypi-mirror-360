.. _examples-label:

Examples
========

Example 1
---------

A CZML document is a list of ``packets``, which have several properties. Recreating the blue box from Cesium sandcastle's `CZML Box <https://sandcastle.cesium.com/?src=CZML%20Box.html&label=CZML>`_::

    from czml3 import Document, Packet, Preamble
    from czml3.properties import (
        Box,
        BoxDimensions,
        Cartesian3Value,
        Color,
        Material,
        Position,
        SolidColorMaterial,
    )
    packet_box = Packet(
        id="my_id",
        position=Position(cartographicDegrees=[-114.0, 40.0, 300000.0]),
        box=Box(
            dimensions=BoxDimensions(
                cartesian=Cartesian3Value(values=[400000.0, 300000.0, 500000.0])
            ),
            material=Material(
                solidColor=SolidColorMaterial(color=Color(rgba=[0, 0, 255, 255]))
            ),
        ),
    )
    doc = Document(
        packets=[Packet(id="document", name="box", version=CZML_VERSION), packet_box]
    )
    print(doc)

This produces the following CZML document::

    [
        {
            "id": "document",
            "name": "box",
            "version": "1.0"
        },
        {
            "id": "my_id",
            "position": {
                "cartographicDegrees": [
                    -114.0,
                    40.0,
                    300000.0
                ]
            },
            "box": {
                "dimensions": {
                    "cartesian": [
                        400000.0,
                        300000.0,
                        500000.0
                    ]
                },
                "material": {
                    "solidColor": {
                        "color": {
                            "rgba": [
                                0.0,
                                0.0,
                                255.0,
                                255.0
                            ]
                        }
                    }
                }
            }
        }
    ]


Example 2
---------

czml3 uses `pydantic <https://docs.pydantic.dev/latest/>`_ for all classes. As such czml3 is able to `coerce data to their right type <https://docs.pydantic.dev/latest/why/#json-schema>`_. For example, the following creates a Position property of doubles using a numpy array of interger type::

    import numpy as np
    from czml3.properties import Position
    print(Position(cartographicDegrees=np.array([-114, 40, 300000], dtype=int)))

This produces the following output::

    {
        "cartographicDegrees": [
            -114.0,
            40.0,
            300000.0
        ]
    }
