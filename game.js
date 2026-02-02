import * as THREE from 'three';
import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';

// ゲーム設定
const BLOCK_SIZE = 1;
const WORLD_SIZE = 32;
const RENDER_DISTANCE = 16;
const GRAVITY = -20;
const JUMP_FORCE = 8;
const MOVE_SPEED = 5;
const PLAYER_HEIGHT = 1.7;
const REACH_DISTANCE = 5;

// ブロックタイプの定義
const BLOCK_TYPES = {
    grass: { color: 0x7CFC00, top: 0x7CFC00, side: 0x8B7355, bottom: 0x654321 },
    dirt: { color: 0x8B7355 },
    stone: { color: 0x808080 },
    wood: { color: 0x8B4513 },
    sand: { color: 0xF4A460 }
};

class MinecraftGame {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.world = new Map();
        this.blocks = new Map();

        // プレイヤー状態
        this.velocity = new THREE.Vector3();
        this.canJump = false;
        this.selectedBlock = 'grass';

        // 入力状態
        this.moveForward = false;
        this.moveBackward = false;
        this.moveLeft = false;
        this.moveRight = false;

        // レイキャスト
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();

        this.init();
    }

    init() {
        // シーンのセットアップ
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x87CEEB);
        this.scene.fog = new THREE.Fog(0x87CEEB, 1, RENDER_DISTANCE * BLOCK_SIZE);

        // カメラのセットアップ
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(WORLD_SIZE / 2, 10, WORLD_SIZE / 2);

        // レンダラーのセットアップ
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.getElementById('game-container').appendChild(this.renderer.domElement);

        // ライトの追加
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
        directionalLight.position.set(50, 100, 50);
        directionalLight.castShadow = true;
        directionalLight.shadow.camera.left = -50;
        directionalLight.shadow.camera.right = 50;
        directionalLight.shadow.camera.top = 50;
        directionalLight.shadow.camera.bottom = -50;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);

        // コントロールのセットアップ
        this.controls = new PointerLockControls(this.camera, document.body);

        const instructions = document.getElementById('instructions');
        instructions.addEventListener('click', () => {
            this.controls.lock();
        });

        this.controls.addEventListener('lock', () => {
            instructions.classList.add('hidden');
            document.getElementById('crosshair').classList.add('visible');
            document.getElementById('block-selector').classList.add('visible');
        });

        this.controls.addEventListener('unlock', () => {
            instructions.classList.remove('hidden');
            document.getElementById('crosshair').classList.remove('visible');
            document.getElementById('block-selector').classList.remove('visible');
        });

        this.scene.add(this.controls.getObject());

        // イベントリスナー
        this.setupEventListeners();

        // 世界の生成
        this.generateWorld();

        // アニメーションループの開始
        this.animate();
    }

    setupEventListeners() {
        // キーボード入力
        document.addEventListener('keydown', (event) => {
            switch (event.code) {
                case 'KeyW':
                    this.moveForward = true;
                    break;
                case 'KeyS':
                    this.moveBackward = true;
                    break;
                case 'KeyA':
                    this.moveLeft = true;
                    break;
                case 'KeyD':
                    this.moveRight = true;
                    break;
                case 'Space':
                    if (this.canJump) {
                        this.velocity.y = JUMP_FORCE;
                        this.canJump = false;
                    }
                    break;
                case 'Digit1':
                    this.selectBlock('grass');
                    break;
                case 'Digit2':
                    this.selectBlock('dirt');
                    break;
                case 'Digit3':
                    this.selectBlock('stone');
                    break;
                case 'Digit4':
                    this.selectBlock('wood');
                    break;
                case 'Digit5':
                    this.selectBlock('sand');
                    break;
            }
        });

        document.addEventListener('keyup', (event) => {
            switch (event.code) {
                case 'KeyW':
                    this.moveForward = false;
                    break;
                case 'KeyS':
                    this.moveBackward = false;
                    break;
                case 'KeyA':
                    this.moveLeft = false;
                    break;
                case 'KeyD':
                    this.moveRight = false;
                    break;
            }
        });

        // マウス入力
        document.addEventListener('mousedown', (event) => {
            if (!this.controls.isLocked) return;

            if (event.button === 0) {
                // 左クリック - ブロック破壊
                this.removeBlock();
            } else if (event.button === 2) {
                // 右クリック - ブロック配置
                this.placeBlock();
            }
        });

        document.addEventListener('contextmenu', (event) => {
            event.preventDefault();
        });

        // ブロック選択UI
        document.querySelectorAll('.block-option').forEach(option => {
            option.addEventListener('click', () => {
                const blockType = option.dataset.type;
                this.selectBlock(blockType);
            });
        });

        // ウィンドウリサイズ
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }

    selectBlock(blockType) {
        this.selectedBlock = blockType;
        document.querySelectorAll('.block-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.type === blockType) {
                option.classList.add('active');
            }
        });
    }

    generateWorld() {
        // シンプルなパーリンノイズ風の地形生成
        for (let x = 0; x < WORLD_SIZE; x++) {
            for (let z = 0; z < WORLD_SIZE; z++) {
                const height = Math.floor(
                    3 +
                    Math.sin(x * 0.1) * 2 +
                    Math.cos(z * 0.1) * 2 +
                    Math.sin(x * 0.05) * Math.cos(z * 0.05) * 3
                );

                // 地形レイヤー
                for (let y = 0; y <= height; y++) {
                    let blockType = 'stone';
                    if (y === height) {
                        blockType = 'grass';
                    } else if (y >= height - 2) {
                        blockType = 'dirt';
                    }

                    this.addBlock(x, y, z, blockType);
                }

                // ランダムな木の生成
                if (Math.random() < 0.02 && height > 3) {
                    const treeHeight = 4 + Math.floor(Math.random() * 2);
                    // 幹
                    for (let y = height + 1; y < height + treeHeight; y++) {
                        this.addBlock(x, y, z, 'wood');
                    }
                    // 葉
                    for (let dx = -2; dx <= 2; dx++) {
                        for (let dz = -2; dz <= 2; dz++) {
                            for (let dy = 0; dy < 3; dy++) {
                                if (Math.abs(dx) === 2 && Math.abs(dz) === 2 && dy < 2) continue;
                                const leafX = x + dx;
                                const leafZ = z + dz;
                                const leafY = height + treeHeight - 1 + dy;
                                if (!(dx === 0 && dz === 0 && dy < 2)) {
                                    this.addBlock(leafX, leafY, leafZ, 'grass');
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    addBlock(x, y, z, type) {
        const key = `${x},${y},${z}`;
        this.world.set(key, type);

        const blockData = BLOCK_TYPES[type];
        const geometry = new THREE.BoxGeometry(BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);

        let materials;
        if (blockData.top) {
            // 草ブロックのような複数面のテクスチャ
            materials = [
                new THREE.MeshLambertMaterial({ color: blockData.side }), // right
                new THREE.MeshLambertMaterial({ color: blockData.side }), // left
                new THREE.MeshLambertMaterial({ color: blockData.top }), // top
                new THREE.MeshLambertMaterial({ color: blockData.bottom }), // bottom
                new THREE.MeshLambertMaterial({ color: blockData.side }), // front
                new THREE.MeshLambertMaterial({ color: blockData.side })  // back
            ];
        } else {
            materials = new THREE.MeshLambertMaterial({ color: blockData.color });
        }

        const block = new THREE.Mesh(geometry, materials);
        block.position.set(
            x * BLOCK_SIZE + BLOCK_SIZE / 2,
            y * BLOCK_SIZE + BLOCK_SIZE / 2,
            z * BLOCK_SIZE + BLOCK_SIZE / 2
        );
        block.castShadow = true;
        block.receiveShadow = true;

        this.scene.add(block);
        this.blocks.set(key, block);
    }

    removeBlockAt(x, y, z) {
        const key = `${x},${y},${z}`;
        if (this.world.has(key)) {
            this.world.delete(key);
            const block = this.blocks.get(key);
            if (block) {
                this.scene.remove(block);
                this.blocks.delete(key);
            }
        }
    }

    getBlockAt(x, y, z) {
        const key = `${x},${y},${z}`;
        return this.world.get(key);
    }

    removeBlock() {
        this.raycaster.setFromCamera(new THREE.Vector2(0, 0), this.camera);
        const intersects = this.raycaster.intersectObjects(Array.from(this.blocks.values()));

        if (intersects.length > 0 && intersects[0].distance < REACH_DISTANCE) {
            const point = intersects[0].point;
            const normal = intersects[0].face.normal;

            const blockPos = new THREE.Vector3(
                Math.floor(point.x - normal.x * 0.5),
                Math.floor(point.y - normal.y * 0.5),
                Math.floor(point.z - normal.z * 0.5)
            );

            this.removeBlockAt(blockPos.x, blockPos.y, blockPos.z);
        }
    }

    placeBlock() {
        this.raycaster.setFromCamera(new THREE.Vector2(0, 0), this.camera);
        const intersects = this.raycaster.intersectObjects(Array.from(this.blocks.values()));

        if (intersects.length > 0 && intersects[0].distance < REACH_DISTANCE) {
            const point = intersects[0].point;
            const normal = intersects[0].face.normal;

            const blockPos = new THREE.Vector3(
                Math.floor(point.x + normal.x * 0.5),
                Math.floor(point.y + normal.y * 0.5),
                Math.floor(point.z + normal.z * 0.5)
            );

            // プレイヤーの位置と重ならないかチェック
            const playerPos = this.controls.getObject().position;
            const distance = blockPos.distanceTo(new THREE.Vector3(
                Math.floor(playerPos.x),
                Math.floor(playerPos.y),
                Math.floor(playerPos.z)
            ));

            if (distance > 1.5) {
                this.addBlock(blockPos.x, blockPos.y, blockPos.z, this.selectedBlock);
            }
        }
    }

    checkCollision(position) {
        const blockX = Math.floor(position.x);
        const blockY = Math.floor(position.y - PLAYER_HEIGHT);
        const blockZ = Math.floor(position.z);

        return this.getBlockAt(blockX, blockY, blockZ) !== undefined;
    }

    updatePhysics(delta) {
        if (!this.controls.isLocked) return;

        // 重力
        this.velocity.y += GRAVITY * delta;

        // 移動
        const direction = new THREE.Vector3();
        const frontVector = new THREE.Vector3(0, 0, Number(this.moveBackward) - Number(this.moveForward));
        const sideVector = new THREE.Vector3(Number(this.moveLeft) - Number(this.moveRight), 0, 0);

        direction.subVectors(frontVector, sideVector).normalize();

        if (this.moveForward || this.moveBackward) {
            this.controls.moveForward(direction.z * MOVE_SPEED * delta);
        }
        if (this.moveLeft || this.moveRight) {
            this.controls.moveRight(direction.x * MOVE_SPEED * delta);
        }

        // 垂直移動
        const position = this.controls.getObject().position;
        position.y += this.velocity.y * delta;

        // 地面との衝突判定
        const groundY = this.getGroundHeight(position.x, position.z) + PLAYER_HEIGHT;
        if (position.y <= groundY) {
            position.y = groundY;
            this.velocity.y = 0;
            this.canJump = true;
        }

        // 世界の境界チェック
        position.x = Math.max(0, Math.min(WORLD_SIZE, position.x));
        position.z = Math.max(0, Math.min(WORLD_SIZE, position.z));
    }

    getGroundHeight(x, z) {
        const blockX = Math.floor(x);
        const blockZ = Math.floor(z);

        for (let y = 20; y >= 0; y--) {
            if (this.getBlockAt(blockX, y, blockZ)) {
                return (y + 1) * BLOCK_SIZE;
            }
        }
        return 0;
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const delta = 0.016; // 約60fps
        this.updatePhysics(delta);

        this.renderer.render(this.scene, this.camera);
    }
}

// ゲームの初期化
const game = new MinecraftGame();
