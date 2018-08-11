init python:
    import math
    
    class ZoomConfig():
        zoomfactor = 1.0
        offset = (0,0)

        @staticmethod
        def reset():
            ZoomConfig.zoomfactor = 1.0
            ZoomConfig.offset = (0,0)

    class Zoomable(renpy.Displayable):
        def __init__(self, child):

            # Pass additional properties on to the renpy.Displayable
            # constructor.
            super(Zoomable, self).__init__()

            # The child.
            self.child = renpy.displayable(child)            
            # The alpha channel of the child.
            self.alpha = 1.0

            # The width and height of us, and our child.
            self.width = 0
            self.height = 0

            # Mouse event tracking
            self.hold = False
            self.moved = False
            self.previous = (0,0)

        def render(self, width, height, st, at):

            # Create a transform, that can adjust the alpha channel of the
            # child.
            t = Transform(child=self.child, alpha=self.alpha)

            # Create a render from the child.
            child_render = renpy.render(t, width, height, st, at)

            # Get the size of the child.
            self.width, self.height = child_render.get_size()

            # Create the render we will return.
            render = renpy.Render(self.width, self.height)

            # Zoom child
            render.zoom(ZoomConfig.zoomfactor, ZoomConfig.zoomfactor)

            # Blit (draw) the child's render to our render.
            render.blit(child_render, ZoomConfig.offset)

            # Return the render.
            return render

        def event(self, ev, x, y, st):
            import pygame

            if ev.type == pygame.MOUSEBUTTONDOWN:
                # if ev.button == 1:
                #     config.keymap['dismiss'].remove('mouseup_1')
                if ev.button == 3:
                    if self.hold == False:
                        self.hold = True
                        self.previous = (x, y)
                if ev.button == 4:
                    self.on_wheel(x, y, "zoom_in")
                    renpy.redraw(self, 0)
                elif ev.button == 5:
                    self.on_wheel(x, y, "zoom_out")
                    renpy.redraw(self, 0)
            elif ev.type == pygame.MOUSEMOTION:
                if self.hold == True:
                    self.drag(x, y)
                    renpy.display.render.redraw(self, 0)
            elif ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 3:
                    self.hold = False
                    if self.moved == True:
                        self.moved = False
                
            return None

        def visit(self):
            return [ self.child ]

        # m_x, m_y: mouse position
        def on_wheel(self, m_x, m_y, zoom_type):
            dx, dy = ZoomConfig.offset

            # Mouse offset to bg
            m_offset_x = m_x - dx
            m_offset_y = m_y - dy

            # Mouse to bg edge ratio
            m_ratio_x = m_offset_x / (self.width * ZoomConfig.zoomfactor)
            m_ratio_y = m_offset_y / (self.height * ZoomConfig.zoomfactor)
            
            if zoom_type == "zoom_in":
                ZoomConfig.zoomfactor = min(ZoomConfig.zoomfactor + 0.02, 2.0)
            else:
                ZoomConfig.zoomfactor = max(ZoomConfig.zoomfactor - 0.02, 1.0)

            new_width = self.width * ZoomConfig.zoomfactor
            new_height = self.height * ZoomConfig.zoomfactor
            dx =  min(m_x - new_width * m_ratio_x, 0)
            dy =  min(m_y - new_height * m_ratio_y, 0)

            dx += max(self.width - new_width - dx, 0)
            dy += max(self.height - new_height - dy, 0)

            ZoomConfig.offset = (dx, dy)

        def drag(self, x, y):
            dx, dy = ZoomConfig.offset
            px, py = self.previous
            m_dx = x - px
            m_dy = y - py
            
            if (m_dx - m_dy != 0) and self.moved == False:
                self.moved = True

            dx = min(dx + m_dx, 0)
            dy = min(dy + m_dy, 0)

            dx += max(self.width * (1 - ZoomConfig.zoomfactor) - dx, 0)
            dy += max(self.height * (1 - ZoomConfig.zoomfactor) - dy, 0)

            self.previous = (x, y)
            ZoomConfig.offset = (dx, dy)