import pygame

class Interface():
    def __init__(self, surface):

        # Общая настройка
        self.display_surface = surface

        # Здоровье
        self.health_bar = pygame.image.load('../Gleb_Runner/images/interface/health_bar.png').convert_alpha()
        self.health_bar_topleft = (54, 39)
        self.bar_max_width = 152
        self.bar_height = 4


        # Биткоины
        self.bitcoin = pygame.image.load('../Gleb_Runner/images/interface/coin.png').convert_alpha()
        self.bitcoin_rect = self.bitcoin.get_rect(topleft=(50, 61))
        self.font = pygame.font.Font('../Gleb_Runner/images/interface/шрифт.ttf', 30)

    # Отображение полоски здоровья
    def show_health(self, current, full):
        self.display_surface.blit(self.health_bar, (20, 10))
        current_health_ratio = current / full
        current_bar_width = self.bar_max_width * current_health_ratio
        heath_bar_rect = pygame.Rect(self.health_bar_topleft, (current_bar_width, self.bar_height))
        pygame.draw.rect(self.display_surface, '#dc4949', heath_bar_rect)

    # Отображение количества собранных биткоинов
    def show_bitcoin(self, amount):
        self.display_surface.blit(self.bitcoin, self.bitcoin_rect)
        bitcoin_amount_surface = self.font.render(str(amount), False, (0, 255, 0))
        bitcoin_amount_rect = bitcoin_amount_surface.get_rect(midleft=(self.bitcoin_rect.right + 4, self.bitcoin_rect.centery))
        self.display_surface.blit(bitcoin_amount_surface, bitcoin_amount_rect)