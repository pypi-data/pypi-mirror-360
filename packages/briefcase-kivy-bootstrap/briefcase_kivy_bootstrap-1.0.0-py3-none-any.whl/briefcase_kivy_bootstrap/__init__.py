"""Briefcase Kivy Bootstrap"""

from briefcase.bootstraps.base import BaseGuiBootstrap


class KivyBootstrap(BaseGuiBootstrap):
    """A bootstrap for Kivy applications."""

    description = "A cross-platform GUI framework for mobile and desktop applications"

    def app_source(self):
        """The Python source code for app.py."""
        return '''\
"""
{{ cookiecutter.description }}
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class {{ cookiecutter.class_name }}App(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = Label(
            text='{{ cookiecutter.formal_name }}',
            size_hint=(1, 0.3),
            font_size='24sp'
        )
        layout.add_widget(title)
        
        # Welcome message
        welcome = Label(
            text='Welcome to your Kivy app!',
            size_hint=(1, 0.4),
            text_size=(None, None),
            halign='center'
        )
        layout.add_widget(welcome)
        
        # Button
        button = Button(
            text='Hello Kivy!',
            size_hint=(1, 0.3),
            on_press=self.on_button_press
        )
        layout.add_widget(button)
        
        return layout
    
    def on_button_press(self, instance):
        instance.text = 'Button Pressed!'


def main():
    {{ cookiecutter.class_name }}App().run()
'''

    def app_start_source(self):
        """The Python source code for __main__.py to start the app."""
        return """\
from {{ cookiecutter.module_name }}.app import main

if __name__ == "__main__":
    main()
"""

    def pyproject_table_briefcase_app_extra_content(self):
        """Additional content for the app section of pyproject.toml."""
        return """
requires = [
    "kivy>=2.3.1",
]
test_requires = [
{% if cookiecutter.test_framework == "pytest" %}
    "pytest",
{% endif %}
]
"""

    def pyproject_table_android(self):
        """Content for Android-specific configuration."""
        return """\
requires = [
    "kivy>=2.3.1",
    "pyjnius",
]
"""

    def pyproject_table_iOS(self):
        """Content for iOS-specific configuration."""
        return """\
requires = [
    "kivy>=2.3.1",
    "rubicon-objc>=0.4.0",
]
"""

    def pyproject_table_macOS(self):
        """Content for macOS-specific configuration."""
        return """\
universal_build = true
requires = [
    "kivy>=2.3.1",
]
"""

    def pyproject_table_linux(self):
        """Content for Linux-specific configuration."""
        return """\
requires = [
    "kivy>=2.3.1",
]
"""

    def pyproject_table_linux_system_debian(self):
        """Content for Debian-specific system requirements."""
        return """\
system_requires = [
    "libgl1-mesa-dev",
    "libgles2-mesa-dev",
    "libmtdev-dev",
    "libsdl2-dev",
    "libsdl2-image-dev",
    "libsdl2-mixer-dev",
    "libsdl2-ttf-dev",
]

system_runtime_requires = [
    "libgl1-mesa-glx",
    "libgles2-mesa",
    "libmtdev1",
    "libsdl2-2.0-0",
    "libsdl2-image-2.0-0",
    "libsdl2-mixer-2.0-0",
    "libsdl2-ttf-2.0-0",
]
"""

    def pyproject_table_linux_system_rhel(self):
        """Content for RHEL-specific system requirements."""
        return """\
system_requires = [
    "mesa-libGL-devel",
    "mesa-libGLES-devel",
    "SDL2-devel",
    "SDL2_image-devel",
    "SDL2_mixer-devel",
    "SDL2_ttf-devel",
]

system_runtime_requires = [
    "mesa-libGL",
    "mesa-libGLES",
    "SDL2",
    "SDL2_image",
    "SDL2_mixer",
    "SDL2_ttf",
]
"""

    def pyproject_table_linux_system_suse(self):
        """Content for SUSE-specific system requirements."""
        return """\
system_requires = [
    "Mesa-libGL-devel",
    "Mesa-libGLESv2-devel",
    "libSDL2-devel",
    "libSDL2_image-devel",
    "libSDL2_mixer-devel",
    "libSDL2_ttf-devel",
]

system_runtime_requires = [
    "Mesa-libGL1",
    "Mesa-libGLESv2-2",
    "libSDL2-2_0-0",
    "libSDL2_image-2_0-0",
    "libSDL2_mixer-2_0-0",
    "libSDL2_ttf-2_0-0",
]
"""

    def pyproject_table_linux_system_arch(self):
        """Content for Arch-specific system requirements."""
        return """\
system_requires = [
    "mesa",
    "sdl2",
    "sdl2_image",
    "sdl2_mixer",
    "sdl2_ttf",
]

system_runtime_requires = [
    "mesa",
    "sdl2",
    "sdl2_image",
    "sdl2_mixer",
    "sdl2_ttf",
]
"""

    def pyproject_table_windows(self):
        """Content for Windows-specific configuration."""
        return """\
requires = [
    "kivy>=2.3.1",
]
"""


__all__ = ["KivyBootstrap"] 