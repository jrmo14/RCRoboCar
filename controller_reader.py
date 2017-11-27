import pygame

pygame.init()
pygame.joystick.init()


class ControllerReader:

    def __init__(self, joystick_id):
        self._joystick = pygame.joystick.Joystick(joystick_id)
        self._joystick.init()

    @property
    def joystick(self):
        # We need to pump the event server so that controller events are processed
        pygame.event.pump()
        return self._joystick

    @staticmethod
    def list_joysticks():
        joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        print("Connected joysticks:")
        for i, joy in enumerate(joysticks):
            joy.init()
            print("ID {}: {}".format(i, joy.get_name()))

    @staticmethod
    def update_events():
        pygame.event.pump()


if __name__ == '__main__':
    ControllerReader.list_joysticks()
