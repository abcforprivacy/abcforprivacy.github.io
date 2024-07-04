const ContinuousCanvasModule = function (max_x, max_y, canvas_width, canvas_height, min_x, min_y) {
    const createElement = (tagName, attrs) => {
        const element = document.createElement(tagName);
        Object.assign(element, attrs);
        return element;
    };

    // Create the element
    const parent = createElement("div", {
        style: `height:${canvas_height}px;`,
        className: "world-grid-parent"
    });

    // Create the tag with absolute positioning
    const canvas = createElement("canvas", {
        width: canvas_width,
        height: canvas_height,
        className: "world-grid"
    });

    // Append it to parent
    parent.appendChild(canvas);

    // Append it to elements
    const elements = document.getElementById("elements");
    elements.appendChild(parent);

    // Create the context for the agents and the drawing controller
    const context = canvas.getContext("2d");

    const canvasDraw = new ContinuousSpaceVisualization(canvas_width, canvas_height, max_x, max_y, min_x, min_y, context);

    this.render = (data) => {
        canvasDraw.resetCanvas();
        for (const layer in data) {
            canvasDraw.drawLayer(data[layer]);
        }
    };

    this.reset = () => {
        canvasDraw.resetCanvas();
    };
};

const ContinuousSpaceVisualization = function (width, height, max_x, max_y, min_x, min_y, context) {
    // Convert the horizontal coordinate to horizontal canvas coordinate
    const xToCanvasCoordinate = (x) => {
        return (x - min_x) / (max_x - min_x) * width;
    };
    // Convert the vertical coordinate to vertical canvas coordinate
    const yToCanvasCoordinate = (y) => {
        return (y - min_y) / (max_y - min_y) * height;
    };

    this.drawLayer = function (portrayalLayer) {
        for (const i in portrayalLayer) {
            const p = portrayalLayer[i];

            // If p.color is a single color string, cast it to an array
            if (!Array.isArray(p.Color)) p.Color = [p.Color];

            // Inverting y, because html5 canvas has y=0 at the top,
            // but we want the origin in the lower left corner
            p.y = min_y + max_y - p.y;

            if (!p.stroke_color) p.stroke_color = p.Color[0];

            // p.xAlign = p.yAlign = 0 means that the agent is centered to it's coordinate
            p.xAlign ??= 0.0;
            p.yAlign ??= 0.0;

            // Call the appropriate drawing function 
            if (p.Shape == "rect") this.drawRectangle(p.x, p.y, p.xAlign, p.yAlign, p.w, p.h, p.Color, p.stroke_color, p.Filled, p.text, p.text_color);
            else if (p.Shape == "circle") this.drawCircle(p.x, p.y, p.xAlign, p.yAlign, p.r, p.Color, p.stroke_color, p.Filled, p.text, p.text_color)
            else if (p.Shape == "arrow") this.drawArrow(p.x, p.y, p.angle, p.w, p.h, p.vector_origin, p.Color, p.stroke_color, p.Filled, p.text, p.text_color);
            else this.drawCustomImage(p.Shape, p.x, p.y, p.size, p.text, p.text_color);
        }
    };

    this.drawRectangle = function (x, y, xAlign, yAlign, w, h, colors, stroke_color, fill, text, text_color) {
        context.beginPath();
        const dx = w / (max_x - min_x) * width;
        const dy = h / (max_y - min_y) * height;

        const x0 = xToCanvasCoordinate(x + xAlign) - dx/2;
        const y0 = yToCanvasCoordinate(y + yAlign) - dy/2;

        context.strokeStyle = stroke_color;
        context.strokeRect(x0, y0, dx, dy);

        if (fill) {
            const gradient = context.createLinearGradient(x0, y0, x0+dx, y0+dy);
            for (let i=0; i<colors.length; i++) {
                gradient.addColorStop(i/colors.length, colors[i]);
            }

            context.fillStyle = gradient;
            context.fillRect(x0, y0, dx, dy);
        }

        if (text !== undefined) {
            context.fillStyle = text_color;
            context.textAlign = "center";
            context.textBaseLine = "middle";
            context.fillText(text, x0 + dx/2, y0 + dy/2);
        }
    };

    this.drawCircle = function (x, y, xAlign, yAlign, radius, colors, stroke_color, fill, text, text_color) {
        const cx = xToCanvasCoordinate(x + xAlign);
        const cy = yToCanvasCoordinate(y + yAlign);

        const rx = radius / (max_x - min_x) * width;
        const ry = radius / (max_y - min_y) * height;

        context.beginPath();
        context.ellipse(cx, cy, rx, ry, 0, 0, 2*Math.PI, false);
        context.closePath();

        context.strokeStyle = stroke_color;
        context.stroke();

        if (fill) {
            const gradient = context.createRadialGradient(cx, cy, rx, cx, cy, 0);
            for (let i=0; i<colors.length; i++) {
                gradient.addColorStop(i/colors.length, colors[i]);
            }
            context.fillStyle = gradient;
            context.fill();
        }

        if (text !== undefined) {
            context.fillStyle = text_color;
            context.textAlign = "center";
            context.textBaseLine = "middle";
            context.fillText(text, cx, cy);
        }
    };

    this.drawArrow = function (x, y, angle, w, l, vector_origin, colors, stroke_color, fill, text, text_color) {
        if (angle === undefined) angle = 0;
        if (l === undefined) l = 1;
        if (w === undefined) w = l/3;
        if (vector_origin === undefined) vector_origin = 0;

        // This is necessary, because in html5 canvas the y=0 is at the top
        angle *= -1;

        // The 7 points of the arrow, when it is drawn horizontally, with the (0,0) point at it's origin.
        const px = [vector_origin, vector_origin, l*0.7+vector_origin, l*0.7+vector_origin, l+vector_origin, l*0.7+vector_origin, l*0.7+vector_origin];
        const py = [-w*0.1875, w*0.1875, w*0.1875, w*0.5, 0, -w*0.5, -w*0.1875];

        context.beginPath();
        // Rotate the coordinate frame of the arrow by the angle and than translate it's origin to (x,y)
        var cx0 = xToCanvasCoordinate(px[0]*Math.cos(angle)-py[0]*Math.sin(angle)+x);
        var cy0 = yToCanvasCoordinate(px[0]*Math.sin(angle)+py[0]*Math.cos(angle)+y);
        var cx1 = cx0;
        var cy1 = cy0;
        context.moveTo(cx0, cy0);
        for (let i=1; i<7; i++) {
            const cx = xToCanvasCoordinate(px[i]*Math.cos(angle)-py[i]*Math.sin(angle)+x);
            const cy = yToCanvasCoordinate(px[i]*Math.sin(angle)+py[i]*Math.cos(angle)+y);
            context.lineTo(cx, cy);

            if (cx < cx0) cx0 = cx;
            else if (cx > cx1) cx1 = cx;
            if (cy < cy0) cy0 = cy;
            else if (cy > cy1) cy1 = cy;
        }
        context.closePath();

        context.strokeStyle = stroke_color;
        context.stroke();

        if (fill) {
            const gradient = context.createLinearGradient(cx0, cy0, cx1, cy1);
            for (let i=0; i<colors.length; i++) {
                gradient.addColorStop(i/colors.length, colors[i]);
            }
            context.fillStyle = gradient;
            context.fill();
        }

        if (text !== undefined) {
            context.fillStyle = text_color;
            context.textAlign = "center";
            context.textBaseLine = "middle";
            context.fillText(text, xToCanvasCoordinate(x), yToCanvasCoordinate(y));
        }
    };

    this.drawCustomImage = function (shape, x, y, size, text, text_color) {
        const img = new Image();
        img.src = "local/custom/".concat(shape);
        if (size === undefined) size = 1;

        const dWidth = size / (max_x - min_x) * width;
        const dHeight = size / (max_y - min_y) * height;
        const cx = xToCanvasCoordinate(x) - dWidth / 2;
        const cy = yToCanvasCoordinate(y) - dHeight / 2;

        const tx = cx + dWidth / 2;
        const ty = cy + dHeight / 2;

        img.onload = function () {
            context.drawImage(img, cx, cy, dWidth, dHeight);
            if (text !== undefined) {
                context.fillStyle = text_color;
                context.textAlign = "center";
                context.textBaseLine = "middle";
                context.fillText(text, tx, ty);
            }
        };
    };

    this.resetCanvas = function () {
        context.clearRect(0, 0, width, height);
        context.beginPath();
    }
};
