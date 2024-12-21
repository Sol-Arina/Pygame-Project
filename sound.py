import pygame


class BaseSound:
    global_volume = 0.5  # Глобальная громкость

    @classmethod
    def set_global_volume(cls, volume):
        """
        Устанавливает глобальную громкость для всех звуков.
        """
        if 0.0 <= volume <= 1.0:
            cls.global_volume = volume
            print(f"Глобальная громкость установлена: {volume}")
        else:
            print("Ошибка: громкость должна быть в диапазоне от 0.0 до 1.0")

    @classmethod
    def get_global_volume(cls):
        """
        Возвращает текущую глобальную громкость.
        """
        return cls.global_volume

    @classmethod
    def adjust_volume(cls, event):
        """
        Изменение громкости музыки клавишами: Ctrl + Up / Ctrl + Down.
        """
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:  # Проверяем, нажата ли Ctrl
                if event.key == pygame.K_UP:  # Ctrl + Up
                    cls.set_global_volume(min(1.0, cls.global_volume + 0.1))  # Увеличиваем громкость
                elif event.key == pygame.K_DOWN:  # Ctrl + Down
                    cls.set_global_volume(max(0.0, cls.global_volume - 0.1))  # Уменьшаем громкость
    

class BackgroundSound(BaseSound):
    def __init__(self, file_name):
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.set_volume(self.global_volume)

    def play(self):
        pygame.mixer.music.play(-1)  # Проигрывание музыки в цикле

    def update_volume(self):
        """
        Обновляет громкость в соответствии с глобальной громкостью.
        """
        pygame.mixer.music.set_volume(BaseSound.global_volume)


class AnimalSound(BaseSound):
    def __init__(self, animal, sound_files):
        """
        :param animal: тип животного ('cow', 'chicken' и т.д.)
        :param sound_files: словарь, где ключ — тип звука, значение — путь к файлу.
        Пример:
        {
            'moo': 'moo.wav',
            'hungry': 'cow_hungry.wav',
            'fed': 'bell.wav',
            'milk': 'milk.wav'
        }
        """
        self.animal = animal
        self.sounds = {
            sound_type: pygame.mixer.Sound(file)
            for sound_type, file in sound_files.items()
        }
        self.update_volume()

    def play(self, sound_type):
        if sound_type in self.sounds:
            self.sounds[sound_type].play()

    def update_volume(self):
        """Обновляет громкость звуков животного в соответствии с глобальной громкостью."""
        for sound in self.sounds.values():
            sound.set_volume(BaseSound.global_volume)


class FarmerSound(BaseSound):
    def __init__(self):
        self.sounds = {
            'steps': pygame.mixer.Sound('steps.wav'),
            'no': pygame.mixer.Sound('no.mp3'), 
            'okay': pygame.mixer.Sound('okay.mp3')
        }
        self.update_volume()
        self.step_duration = 200  # Длительность звука шагов в миллисекундах

    def play(self, sound):
        if sound in self.sounds:
            # Для звука шагов задаем максимальную продолжительность воспроизведения
            if sound == 'steps':
                self.sounds[sound].play(maxtime=self.step_duration)
            else:
                self.sounds[sound].play()

    def update_volume(self):
        """Обновляет громкость звуков фермера согласно глобальной громкости."""
        for sound in self.sounds.values():
            sound.set_volume(BaseSound.global_volume)  # Используем глобальную громкость из BaseSound

    def stop(self, sound):
        """Останавливает звук, если он еще играет."""
        if sound in self.sounds:
            self.sounds[sound].stop()