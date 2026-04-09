"""트랙 생성 - 도로, 잔디, 장애물"""
import random
from ursina import Entity, color, Vec3


class TrackSegment(Entity):
    """도로 세그먼트 (길이 20 단위)"""
    def __init__(self, z_pos, **kwargs):
        super().__init__(**kwargs)
        self.z_start = z_pos

        # 도로
        self.road = Entity(
            parent=self,
            model='cube',
            color=color.rgb(100, 100, 110),
            scale=(10, 0.1, 20),
            position=(0, 0, z_pos),
        )

        # 도로 중앙선
        self.center_line = Entity(
            parent=self,
            model='cube',
            color=color.rgb(255, 214, 0),
            scale=(0.15, 0.11, 18),
            position=(0, 0.01, z_pos),
        )

        # 양쪽 잔디
        self.grass_left = Entity(
            parent=self,
            model='cube',
            color=color.rgb(76, 175, 80),
            scale=(20, 0.1, 20),
            position=(-15, 0, z_pos),
        )
        self.grass_right = Entity(
            parent=self,
            model='cube',
            color=color.rgb(76, 175, 80),
            scale=(20, 0.1, 20),
            position=(15, 0, z_pos),
        )

        # 도로 가장자리
        self.edge_left = Entity(
            parent=self,
            model='cube',
            color=color.rgb(255, 255, 255),
            scale=(0.2, 0.11, 20),
            position=(-5, 0.01, z_pos),
        )
        self.edge_right = Entity(
            parent=self,
            model='cube',
            color=color.rgb(255, 255, 255),
            scale=(0.2, 0.11, 20),
            position=(5, 0.01, z_pos),
        )

        # 장식: 나무 (랜덤)
        self.trees = []
        for _ in range(random.randint(1, 3)):
            side = random.choice([-1, 1])
            tree_x = side * random.uniform(7, 12)
            trunk = Entity(
                parent=self,
                model='cube',
                color=color.rgb(139, 90, 43),
                scale=(0.4, 1.5, 0.4),
                position=(tree_x, 0.75, z_pos + random.uniform(-8, 8)),
            )
            leaves = Entity(
                parent=self,
                model='cube',
                color=color.rgb(56, 142, 60),
                scale=(1.2, 1.2, 1.2),
                position=(tree_x, 2, z_pos + random.uniform(-8, 8)),
            )
            self.trees.extend([trunk, leaves])

        # 장애물
        self.obstacles = []

    def destroy_segment(self):
        """세그먼트 삭제"""
        for t in self.trees:
            t.enabled = False
        for o in self.obstacles:
            o.enabled = False
        self.road.enabled = False
        self.center_line.enabled = False
        self.grass_left.enabled = False
        self.grass_right.enabled = False
        self.edge_left.enabled = False
        self.edge_right.enabled = False
        self.enabled = False


class Obstacle(Entity):
    """장애물"""
    def __init__(self, obstacle_type='cone', **kwargs):
        self.obstacle_type = obstacle_type

        if obstacle_type == 'cone':
            super().__init__(
                model='cube',
                color=color.rgb(251, 140, 0),
                scale=(0.4, 0.8, 0.4),
                **kwargs,
            )
        elif obstacle_type == 'car':
            super().__init__(
                model='cube',
                color=color.random_color(),
                scale=(1.2, 0.8, 2),
                **kwargs,
            )
        elif obstacle_type == 'barricade':
            super().__init__(
                model='cube',
                color=color.rgb(229, 57, 53),
                scale=(3, 0.6, 0.3),
                **kwargs,
            )


class Track:
    """트랙 매니저 - 세그먼트 생성/삭제"""
    def __init__(self):
        self.segments = []
        self.segment_length = 20
        self.segments_ahead = 10
        self.segments_behind = 3
        self.last_generated_z = -self.segment_length
        self.obstacle_interval = 3  # 3세그먼트마다 장애물
        self.segment_count = 0

        # 초기 트랙 생성
        for i in range(self.segments_ahead):
            self.generate_segment()

    def generate_segment(self):
        """새 세그먼트 생성"""
        z = self.last_generated_z + self.segment_length
        seg = TrackSegment(z)
        self.segment_count += 1

        # 일정 간격으로 장애물 배치
        if self.segment_count > 2 and self.segment_count % self.obstacle_interval == 0:
            self.spawn_obstacles(seg, z)

        self.segments.append(seg)
        self.last_generated_z = z

    def spawn_obstacles(self, segment, z):
        """세그먼트에 장애물 배치"""
        num = random.randint(1, 3)
        types = ['cone', 'cone', 'cone', 'car', 'car', 'barricade']

        for _ in range(num):
            otype = random.choice(types)
            x = random.uniform(-3.5, 3.5)
            z_offset = random.uniform(-8, 8)

            obs = Obstacle(
                obstacle_type=otype,
                position=(x, 0.4, z + z_offset),
            )
            segment.obstacles.append(obs)

    def update(self, player_z):
        """플레이어 위치 기반으로 세그먼트 생성/삭제"""
        # 앞쪽 세그먼트 생성
        while self.last_generated_z < player_z + self.segments_ahead * self.segment_length:
            self.generate_segment()

        # 뒤쪽 세그먼트 삭제
        cutoff = player_z - self.segments_behind * self.segment_length
        to_remove = []
        for seg in self.segments:
            if seg.z_start < cutoff:
                seg.destroy_segment()
                to_remove.append(seg)

        for seg in to_remove:
            self.segments.remove(seg)

    def check_collision(self, bike_pos, bike_scale=(0.8, 0.5, 1.5)):
        """바이크와 장애물 충돌 체크 (AABB)"""
        bx, bz = bike_pos.x, bike_pos.z
        bw, bl = bike_scale[0] / 2, bike_scale[2] / 2

        for seg in self.segments:
            for obs in seg.obstacles:
                if not obs.enabled:
                    continue
                ox, oz = obs.x, obs.z
                ow = obs.scale_x / 2
                ol = obs.scale_z / 2

                if (abs(bx - ox) < bw + ow and
                    abs(bz - oz) < bl + ol):
                    return True
        return False
