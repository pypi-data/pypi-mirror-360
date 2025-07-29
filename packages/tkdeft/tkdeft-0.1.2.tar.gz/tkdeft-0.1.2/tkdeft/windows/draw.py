class DDraw(object):
    def create_svg_image(self, path, path2=None, way=0):
        if way == 0:
            return self.create_tksvg_image(path)
        elif way == 1:
            return self.create_wand_image(path, path2)
    def create_tksvg_image(self, path):
        from tksvg import SvgImage
        tkimage = SvgImage(file=path)
        return tkimage

    def create_tk_image(self, path):
        from PIL.Image import open
        from PIL.ImageTk import PhotoImage
        image = open(path)
        self.tkimage = PhotoImage(image=image)
        return self.tkimage

    def create_wand_image(self, input_path, output_path):
        from wand.image import Image
        from wand.exceptions import ImageError
        from tkinter import PhotoImage

        try:
            with Image(filename=input_path, background="transparent") as img:
                img.format = "png"
                img.save(filename=output_path)

            photoimg = PhotoImage(file=output_path)
        except ImageError:
            return None
        else:
            return photoimg


class DSvgDraw(DDraw):
    def temppath(self, path=None, suffix='.svg'):
        if not path:
            from tempfile import mkstemp
            _, path = mkstemp(suffix=suffix, prefix="tkdeft.temp.")
        return path

    def create_drawing(self, width, height, temppath=None, **kwargs):
        path = self.temppath(temppath)
        import svgwrite
        dwg = svgwrite.Drawing(path, width=width, height=height, **kwargs)

        return path, dwg
