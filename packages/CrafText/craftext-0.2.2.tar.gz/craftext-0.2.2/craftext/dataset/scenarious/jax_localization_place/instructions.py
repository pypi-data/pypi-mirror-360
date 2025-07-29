from craftext.environment.scenarious.checkers.target_state import TargetState, LocalizaPlacingState
from craftext.environment.craftext_constants import Scenarios, BlockType

def create_target_state(object_inventory_enum, object_to_place, count_to_collect, count_to_stand):
    target_achievements = LocalizaPlacingState(object_inventory_enum, object_to_place, count_to_collect, count_to_stand)
    return TargetState(Localization_placing=target_achievements)


# one = {"one_1": {
#         'instruction': "Put a crafting table 1 step above the tree.",
#         'instruction_paraphrases': [
#             "Place a crafting table one tile above the tree.",
#             "Position a crafting table exactly one block up from the tree.",
#             "Set up a crafting table one unit away from the tree, above it.",
#             "Arrange a crafting table one step above the tree.",
#             "Put a crafting table one tile away from the tree, on top."
#         ],
#         'check_lambda': lambda game_data, ix: place_object_relevant_to(
#             game_data, BlockType.CRAFTING_TABLE, BlockType.TREE, 2, 1
#         ),
#         'complexity': "medium-pease"
#     },
#        "one_2": {
#         'instruction': "Put a crafting table 1 step above the tree.",
#         'instruction_paraphrases': [
#             "Place a crafting table one tile above the tree.",
#             "Position a crafting table exactly one block up from the tree.",
#             "Set up a crafting table one unit away from the tree, above it.",
#             "Arrange a crafting table one step above the tree.",
#             "Put a crafting table one tile away from the tree, on top."
#         ],
#         'check_lambda': lambda game_data, ix: place_object_relevant_to(
#             game_data, BlockType.CRAFTING_TABLE, BlockType.TREE, 2, 1
#         ),
#         'complexity': "medium-pease"
#     },
#       }
medium = {
    "INSTRUCTION_PLACE_STONE_FURNACE_1_1": {
        "instruction": "Place a stone one block to the left of the furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put a stone block just left of the smelter.",
            "To the immediate left of the heating station, deposit a piece of rock.",
            "Beside the furnace, specifically to its left, position a stone block.",
            "In relation to the foundry, ensure there's a stone one square to the left of it.",
            "One space to the left of the apparatus for smelting ore, situate a piece of stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.FURNACE, 1, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_GRASS_2_3": {
        "instruction": "Place a plant three blocks above the grass",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position a plant object three units to the top of the grassy patch",
            "Put the plant item three spaces upward from the area with grass",
            "On the grass, ensure there is a plant three blocks in the upward direction",
            "Create a distance of three blocks from the grass to the top and place the plant there",
            "Set a plant three blocks to the north of the grass location"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.GRASS, 2, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_IRON_2_2": {
        "instruction": "Place a stone two blocks above the iron.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put a rock two places upwards from the iron.",
            "Above the iron, position a stone two blocks distance away.",
            "Two blocks further upward from the iron, situate a stone.",
            "Relocate a stone to a spot two blocks in the northern direction from the iron.",
            "In relation to the iron, a rock needs to be placed in a position which is two blocks height above."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.IRON, 2, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_COAL_1_4": {
        "instruction": "Place the stone 4 blocks to the left of the coal.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the stone 4 blocks left from the coal.",
            "Position the rock 4 squares to the left of the coal.",
            "Situate the stone four paces to the west of the coal deposit.",
            "Arrange the piece of stone 4 square-spaces in the westerly direction from the coal.",
            "Align the rock accordingly such that its position is exactly 4 units left of the coal."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.COAL, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_PLANT_2_3": {
        "instruction": "Please place the Crafting Table three blocks north from the Plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you put the workbench three squares above the plant?",
            "I'd appreciate it if you positioned the Craft Table three spots north of the flora.",
            "The Crafting Desk needs to be arranged three units to the top from the vegetation.",
            "Kindly position the Artisan Table at a space of three blocks towards the upward direction from the Plant.",
            "Could you ensure the placement of the Manufacturer's Desk to be on the vertically upward side from the Plant at a space of three blocks?"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.PLANT, 2, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_COAL_2_1": {
        "instruction": "Place a stone 1 block above the coal",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put a rock exactly one block on top of the coal deposit",
            "Against the coal, position a stone exactly a block higher",
            "Prop up a stone single block over the carbon",
            "Atop the coal, situate a slab of stone precisely one block up",
            "Establish a single block gap between the placed stone and the existing coal"
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.COAL, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_TREE_2_4": {
        "instruction": "Place the stone 4 blocks above the tree",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the stone four blocks to the top of the tree",
            "Move stone 4 blocks over the tree",
            "Ensure the stone is set four blocks on top of tree denoted spot",
            "Situate the stone precisely four blocks high from the tree",
            "Above the known tree position, correctly position the stone four blocks higher"
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.TREE, 2, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_STONE_0_4": {
        "instruction": "[medium] PLACE STONE 4 BLOCKS TO THE RIGHT OF STONE",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "[SIMPLE TASK] POSITION A ROCK FOUR SQUARES TO THE RIGHT OF ANOTHER ROCK",
            "[BASIC LEVEL] ARRANGE A STONE QUAD TO THE RIGHT SIDE RELATIVE TO STONE",
            "[ELEMENTARY LEVEL] SETUP A BOULDER JUST FOUR SQUARES RIGHTWARD FROM ANOTHER BOULDER",
            "[BEGINNER] MAKE A STONE POSITIONING FOUR BLOCKS FROM THE RIGHT SIDE OF AN EXISTING STONE",
            "[LOW DIFICULTY] ESTABLISH A STONE'S LOCATION FOUR SPACES TO THE RIGHT OF A STONE CURRENTLY IN PLACE"
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.STONE, 0, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_TREE_3_5": {
        "instruction": "Place the stone five blocks below the tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "You need to situate the rock five blocks beneath the timber.",
            "Can you position the stone five spaces under the sapling?",
            "It's required to locate the gemstone five places down from the woody plant.",
            "Would you mind laying the boulder down five blocks from the bottom of the pine tree?",
            "Could you arrange the mineral block at a distance of five spaces directly below the oak tree?"
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.TREE, 3, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_STONE_1_2": {
        "instruction": "Place a stone, two units to the left of another stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Could you put a stone two blocks left from another rock?",
            "Locate a stone and then place another piece of stone two spots to the left of it.",
            "Find a stone and subsequently drop another stone two spaces to its left.",
            "Identify a stone and set another stone exactly two blocks leftwards.",
            "Discover a rock and then position one more stone accurately two units left of it."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.STONE, 1, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_STONE_1_4": {
        "instruction": "Place a furnace 4 blocks to the left of the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate a furnace four squares to the left of the rock.",
            "Position the oven four blocks leftward of the stone.",
            "Locate the heating unit four units on the stone's left.",
            "Set the cooker to the fourth square on the left side of the boulder.",
            "Adjacent to the fourth block on the stone's left, install a furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.STONE, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_WATER_2_1": {
        "instruction": "Place a plant one block above the water",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "One block over the water, you need to set a plant down",
            "To the water's immediate top, install a plant block",
            "Directly above the body of water, deposit a botanical block",
            "In the spot right over the water, position a flora cube",
            "In the slot right above the aquatic element, place a verdant square"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.WATER, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_PATH_1_5": {
        "instruction": "Place crafting table 5 blocks to the left of the path",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the left side of the path, position the crafting table five blocks away",
            "Ensure the crafting table is situated five blocks left from the path",
            "Position the workbench at a location that is five blocks to the left of the path",
            "Make sure the crafting table is five blocks to the left of the path",
            "Establish a crafting table five units left from the path"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.PATH, 1, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_COAL_1_1": {
        "instruction": "Place the crafting table one block to the left of the coal",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "You need to position the workbench exactly one block left of the coal",
            "One block to the coal's left, that's where the crafting station should be",
            "Place the crafting table to the left side of the coal with a distance of one block",
            "Set up the workbench on the coal's left exactly one block away",
            "The coal should be one block to the right of the crafting table. Put the crafting table accordingly"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.COAL, 1, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_GRASS_3_1": {
        "instruction": "Position a Plant exactly one block below a patch of Grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate a Plant directly one block beneath some Grassland.",
            "Beneath a piece of Turf, place a Plant precisely one block away.",
            "One block downwards from a green Grass area, establish a Plant.",
            "Arrange for a Plant to be exactly one block below a Grass square on the map.",
            "Ensure a Plant is positioned right single block beneath a verdant Grassland."
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.GRASS, 3, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_FURNACE_0_5": {
        "instruction": "Place the Plant 5 blocks to the right of the Furnace",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the right side of the Furnace, position the Plant 5 blocks away",
            "Kindly set the Plant at a distance of 5 blocks to the right from the Furnace",
            "At a gap of 5 blocks to the right from the Furnace, please put down the Plant",
            "Locate the Plant 5 spaces to the right of the Furnace",
            "From the Furnace, travel 5 blocks to the right and there put the Plant"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.FURNACE, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_0_5": {
        "instruction": "Place the crafting table 5 blocks to the right of the water.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Please put the crafting table 5 squares away on the right side of the water.",
            "Could you position the workbench five blocks to the right from the lake, please?",
            "Would you mind setting the bench five to the right of the water?",
            "The crafting table needs to be laid down five blocks to the east of the water.",
            "Can you arrange for the bench to be set five blocks directly right of the water source?"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_1_4": {
        "instruction": "Place the crafting table 4 blocks to the left side of the water",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Set the workbench four slots to the left of the water source",
            "Position the crafting station to the left, exactly four blocks from the water",
            "Situate the crafting table four blocks to the left of the water body",
            "Put the workshop table towards the left, maintaining a distance of four blocks from the water"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_1_2": {
        "instruction": "Place the furnace 2 blocks to the left of the existing furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace two blocks left of the current one.",
            "Position the furnace a gap of two blocks left from the present furnace.",
            "Establish the furnace two blocks leftward from the current furnace.",
            "Put the furnace two blocks to the left side of the furnace already present.",
            "Locate the furnace two blocks towards the left of the old furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 1, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_STONE_3_5": {
        "instruction": "Place the plant five blocks beneath the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Plant the plant five blocks below the rock.",
            "Position the greenery five blocks underneath the boulder.",
            "Put the flora five blocks down from the pebble.",
            "Need you to situate the vegetation five blocks under the cobblestone.",
            "Could you please sit the sapling five blocks downwards from the granite?"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.STONE, 3, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_TREE_0_2": {
        "instruction": "Place a stone 2 blocks to the right of a tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "To the right of a tree, put a stone two blocks away.",
            "Next to the tree, position a stone two blocks to the right.",
            "Directly two blocks right of a tree, you need to place a stone.",
            "Two square lengths to the right from a tree, set down a stone.",
            "At a distance of two blocks rightwards from the tree, deposit a stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.TREE, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_2_1": {
        "instruction": "Place the furnace 1 block top of another furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace one block above a pre-existing furnace.",
            "Arrange a furnace one block higher than another furnace.",
            "Install a furnace a block above another furnace.",
            "Position a furnace one block ahead on top of another.",
            "Put the furnace one block ahead above another furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_STONE_1_5": {
        "instruction": "Place the crafting table five blocks to the left of the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench five steps left from the rock.",
            "Locate the stone, then place the craftsman's table five blocks to its left.",
            "Situate the carpenter's bench five blocks to the west of the cobblestone.",
            "Find the boulder and install the artisan's flat surface five strides to its port side.",
            "On the offshore side from the pebble, station the joiner's work surface at a distance of five blocks."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.STONE, 1, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_TREE_2_1": {
        "instruction": "Place the crafting table one block to the top of the tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench a block above the tree.",
            "The crafting table should be positioned one block higher than the tree.",
            "Set the workbench one level upward from the tree.",
            "Put the crafting station one block towards the sky from the tree.",
            "Position the workbench above the tree at a distance of a single block."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.TREE, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_TREE_0_1": {
        "instruction": "Place the furnace one block to the right of the tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the burner one brick away to the carriage hand of the arboreal structure.",
            "Position the heater precisely one cube to the east of the wooded tract.",
            "Locate the kiln a single stone's distance to the right side of the timber source.",
            "Position the heat source a space to the starboard of the tree.",
            "Situate the oven at one unit of distance to the right of the sylvan being."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.TREE, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_DIAMOND_2_5": {
        "instruction": "Place the furnace five blocks to the top of the diamond",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you position the furnace exactly five blocks above the diamond?",
            "Set the furnace five blocks north from the diamond",
            "Could you set the diamond, then move five blocks up and place the furnace there?",
            "Make sure the furnace is situated five blocks upward from the diamond",
            "Five blocks to the top from the diamond, I want you to put down the furnace"
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.DIAMOND, 2, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PATH_0_1": {
        "instruction": "Please place the stone 1 block to the right of the pathway.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you put the stone exactly one block right next to the path, please?",
            "On the right side of our path, one block away, I need you to position the stone.",
            "Next to our path, but keeping it one block away, and specifically on the right side, can you install the stone there?",
            "Locate the pathway and then go right one block. That's where I'd appreciate if you can place the stone.",
            "Identify the path first. Move one step right from it, and that’s your spot to put the stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PATH, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PATH_2_3": {
        "instruction": "Place furnace 3 blocks to the top of the path.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Three blocks above the path, put a furnace.",
            "Find a path and place a furnace 3 blocks above it.",
            "Go 3 blocks north of a path and there, position a furnace.",
            "On the path, move 3 blocks upwards. There, you should deposit a furnace.",
            "Identify a path and from there, shift three spaces beyond. The location should be perfect for setting up a furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PATH, 2, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PLANT_0_2": {
        "instruction": "Place the stone 2 blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the rock two blocks to the right from the flora.",
            "Establish the stone exactly two squares on the right side of the vegetation.",
            "Set the stone two units towards the right of the herbage.",
            "Arrange the cobble to be two blocks rightward of the shrubbery.",
            "Locate the boulder a couple of blocks on the right-hand side of the greenery."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PLANT, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PLANT_0_3": {
        "instruction": "Place the furnace three blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace to the right of the plant, keeping a distance of three blocks.",
            "On the right side of the plant, maintain a three-block distance and place the furnace there.",
            "Three blocks to the right of the plant, that's where the furnace should be situated.",
            "Establish the location of the furnace three blocks directly right from the plant.",
            "To the exact right of the plant and three blocks away, position the furnace there."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PLANT, 0, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_COAL_1_4": {
        "instruction": "Place the crafting table four blocks to the left of the coal",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench four blocks left from the piece of coal",
            "Position the crafting station a distance of four blocks to the left of the lump of coal",
            "I need you to place the crafting table exactly four squares to the left of the coal block",
            "Could you position the artisan table four segments westwards of the coal deposit?",
            "Make sure you place the crafting table four units to the left of the coal chunk."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.COAL, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_GRASS_3_1": {
        "instruction": "Position a Plant exactly one block below a patch of Grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate a Plant directly one block beneath some Grassland.",
            "Beneath a piece of Turf, place a Plant precisely one block away.",
            "One block downwards from a green Grass area, establish a Plant.",
            "Arrange for a Plant to be exactly one block below a Grass square on the map.",
            "Ensure a Plant is positioned right single block beneath a verdant Grassland."
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.GRASS, 3, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_FURNACE_0_5": {
        "instruction": "Place the Plant 5 blocks to the right of the Furnace",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the right side of the Furnace, position the Plant 5 blocks away",
            "Kindly set the Plant at a distance of 5 blocks to the right from the Furnace",
            "At a gap of 5 blocks to the right from the Furnace, please put down the Plant",
            "Locate the Plant 5 spaces to the right of the Furnace",
            "From the Furnace, travel 5 blocks to the right and there put the Plant"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.FURNACE, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_0_5": {
        "instruction": "Place the crafting table 5 blocks to the right of the water.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Please put the crafting table 5 squares away on the right side of the water.",
            "Could you position the workbench five blocks to the right from the lake, please?",
            "Would you mind setting the bench five to the right of the water?",
            "The crafting table needs to be laid down five blocks to the east of the water.",
            "Can you arrange for the bench to be set five blocks directly right of the water source?"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_1_4": {
        "instruction": "Place the crafting table 4 blocks to the left side of the water",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Set the workbench four slots to the left of the water source",
            "Position the crafting station to the left, exactly four blocks from the water",
            "Situate the crafting table four blocks to the left of the water body",
            "Put the workshop table towards the left, maintaining a distance of four blocks from the water"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_1_2": {
        "instruction": "Place the furnace 2 blocks to the left of the existing furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace two blocks left of the current one.",
            "Position the furnace a gap of two blocks left from the present furnace.",
            "Establish the furnace two blocks leftward from the current furnace.",
            "Put the furnace two blocks to the left side of the furnace already present.",
            "Locate the furnace two blocks towards the left of the old furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 1, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_STONE_3_5": {
        "instruction": "Place the plant five blocks beneath the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Plant the plant five blocks below the rock.",
            "Position the greenery five blocks underneath the boulder.",
            "Put the flora five blocks down from the pebble.",
            "Need you to situate the vegetation five blocks under the cobblestone.",
            "Could you please sit the sapling five blocks downwards from the granite?"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.STONE, 3, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_TREE_0_2": {
        "instruction": "Place a stone 2 blocks to the right of a tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "To the right of a tree, put a stone two blocks away.",
            "Next to the tree, position a stone two blocks to the right.",
            "Directly two blocks right of a tree, you need to place a stone.",
            "Two square lengths to the right from a tree, set down a stone.",
            "At a distance of two blocks rightwards from the tree, deposit a stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.TREE, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_2_1": {
        "instruction": "Place the furnace 1 block top of another furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace one block above a pre-existing furnace.",
            "Arrange a furnace one block higher than another furnace.",
            "Install a furnace a block above another furnace.",
            "Position a furnace one block ahead on top of another.",
            "Put the furnace one block ahead above another furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_STONE_1_5": {
        "instruction": "Place the crafting table five blocks to the left of the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench five steps left from the rock.",
            "Locate the stone, then place the craftsman's table five blocks to its left.",
            "Situate the carpenter's bench five blocks to the west of the cobblestone.",
            "Find the boulder and install the artisan's flat surface five strides to its port side.",
            "On the offshore side from the pebble, station the joiner's work surface at a distance of five blocks."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.STONE, 1, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_TREE_2_1": {
        "instruction": "Place the crafting table one block to the top of the tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench a block above the tree.",
            "The crafting table should be positioned one block higher than the tree.",
            "Set the workbench one level upward from the tree.",
            "Put the crafting station one block towards the sky from the tree.",
            "Position the workbench above the tree at a distance of a single block."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.TREE, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_TREE_0_1": {
        "instruction": "Place the furnace one block to the right of the tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the burner one brick away to the carriage hand of the arboreal structure.",
            "Position the heater precisely one cube to the east of the wooded tract.",
            "Locate the kiln a single stone's distance to the right side of the timber source.",
            "Position the heat source a space to the starboard of the tree.",
            "Situate the oven at one unit of distance to the right of the sylvan being."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.TREE, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_DIAMOND_2_5": {
        "instruction": "Place the furnace five blocks to the top of the diamond",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you position the furnace exactly five blocks above the diamond?",
            "Set the furnace five blocks north from the diamond",
            "Could you set the diamond, then move five blocks up and place the furnace there?",
            "Make sure the furnace is situated five blocks upward from the diamond",
            "Five blocks to the top from the diamond, I want you to put down the furnace"
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.DIAMOND, 2, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PATH_0_1": {
        "instruction": "Please place the stone 1 block to the right of the pathway.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you put the stone exactly one block right next to the path, please?",
            "On the right side of our path, one block away, I need you to position the stone.",
            "Next to our path, but keeping it one block away, and specifically on the right side, can you install the stone there?",
            "Locate the pathway and then go right one block. That's where I'd appreciate if you can place the stone.",
            "Identify the path first. Move one step right from it, and that’s your spot to put the stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PATH, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PATH_2_3": {
        "instruction": "Place furnace 3 blocks to the top of the path.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Three blocks above the path, put a furnace.",
            "Find a path and place a furnace 3 blocks above it.",
            "Go 3 blocks north of a path and there, position a furnace.",
            "On the path, move 3 blocks upwards. There, you should deposit a furnace.",
            "Identify a path and from there, shift three spaces beyond. The location should be perfect for setting up a furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PATH, 2, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PLANT_0_2": {
        "instruction": "Place the stone 2 blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the rock two blocks to the right from the flora.",
            "Establish the stone exactly two squares on the right side of the vegetation.",
            "Set the stone two units towards the right of the herbage.",
            "Arrange the cobble to be two blocks rightward of the shrubbery.",
            "Locate the boulder a couple of blocks on the right-hand side of the greenery."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PLANT, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PLANT_0_3": {
        "instruction": "Place the furnace three blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace to the right of the plant, keeping a distance of three blocks.",
            "On the right side of the plant, maintain a three-block distance and place the furnace there.",
            "Three blocks to the right of the plant, that's where the furnace should be situated.",
            "Establish the location of the furnace three blocks directly right from the plant.",
            "To the exact right of the plant and three blocks away, position the furnace there."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PLANT, 0, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_COAL_1_4": {
        "instruction": "Place the crafting table four blocks to the left of the coal",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench four blocks left from the piece of coal",
            "Position the crafting station a distance of four blocks to the left of the lump of coal",
            "I need you to place the crafting table exactly four squares to the left of the coal block",
            "Could you position the artisan table four segments westwards of the coal deposit?",
            "Make sure you place the crafting table four units to the left of the coal chunk."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.COAL, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_GRASS_3_1": {
        "instruction": "Position a Plant exactly one block below a patch of Grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate a Plant directly one block beneath some Grassland.",
            "Beneath a piece of Turf, place a Plant precisely one block away.",
            "One block downwards from a green Grass area, establish a Plant.",
            "Arrange for a Plant to be exactly one block below a Grass square on the map.",
            "Ensure a Plant is positioned right single block beneath a verdant Grassland."
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.GRASS, 3, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_FURNACE_0_5": {
        "instruction": "Place the Plant 5 blocks to the right of the Furnace",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the right side of the Furnace, position the Plant 5 blocks away",
            "Kindly set the Plant at a distance of 5 blocks to the right from the Furnace",
            "At a gap of 5 blocks to the right from the Furnace, please put down the Plant",
            "Locate the Plant 5 spaces to the right of the Furnace",
            "From the Furnace, travel 5 blocks to the right and there put the Plant"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.FURNACE, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_0_5": {
        "instruction": "Place the crafting table 5 blocks to the right of the water.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Please put the crafting table 5 squares away on the right side of the water.",
            "Could you position the workbench five blocks to the right from the lake, please?",
            "Would you mind setting the bench five to the right of the water?",
            "The crafting table needs to be laid down five blocks to the east of the water.",
            "Can you arrange for the bench to be set five blocks directly right of the water source?"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_1_4": {
        "instruction": "Place the crafting table 4 blocks to the left side of the water",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Set the workbench four slots to the left of the water source",
            "Position the crafting station to the left, exactly four blocks from the water",
            "Situate the crafting table four blocks to the left of the water body",
            "Put the workshop table towards the left, maintaining a distance of four blocks from the water"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_1_2": {
        "instruction": "Place the furnace 2 blocks to the left of the existing furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace two blocks left of the current one.",
            "Position the furnace a gap of two blocks left from the present furnace.",
            "Establish the furnace two blocks leftward from the current furnace.",
            "Put the furnace two blocks to the left side of the furnace already present.",
            "Locate the furnace two blocks towards the left of the old furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 1, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_STONE_3_5": {
        "instruction": "Place the plant five blocks beneath the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Plant the plant five blocks below the rock.",
            "Position the greenery five blocks underneath the boulder.",
            "Put the flora five blocks down from the pebble.",
            "Need you to situate the vegetation five blocks under the cobblestone.",
            "Could you please sit the sapling five blocks downwards from the granite?"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.STONE, 3, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_TREE_0_2": {
        "instruction": "Place a stone 2 blocks to the right of a tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "To the right of a tree, put a stone two blocks away.",
            "Next to the tree, position a stone two blocks to the right.",
            "Directly two blocks right of a tree, you need to place a stone.",
            "Two square lengths to the right from a tree, set down a stone.",
            "At a distance of two blocks rightwards from the tree, deposit a stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.TREE, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_2_1": {
        "instruction": "Place the furnace 1 block top of another furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace one block above a pre-existing furnace.",
            "Arrange a furnace one block higher than another furnace.",
            "Install a furnace a block above another furnace.",
            "Position a furnace one block ahead on top of another.",
            "Put the furnace one block ahead above another furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_STONE_1_5": {
        "instruction": "Place the crafting table five blocks to the left of the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench five steps left from the rock.",
            "Locate the stone, then place the craftsman's table five blocks to its left.",
            "Situate the carpenter's bench five blocks to the west of the cobblestone.",
            "Find the boulder and install the artisan's flat surface five strides to its port side.",
            "On the offshore side from the pebble, station the joiner's work surface at a distance of five blocks."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.STONE, 1, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_TREE_2_1": {
        "instruction": "Place the crafting table one block to the top of the tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench a block above the tree.",
            "The crafting table should be positioned one block higher than the tree.",
            "Set the workbench one level upward from the tree.",
            "Put the crafting station one block towards the sky from the tree.",
            "Position the workbench above the tree at a distance of a single block."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.TREE, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_TREE_0_1": {
        "instruction": "Place the furnace one block to the right of the tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the burner one brick away to the carriage hand of the arboreal structure.",
            "Position the heater precisely one cube to the east of the wooded tract.",
            "Locate the kiln a single stone's distance to the right side of the timber source.",
            "Position the heat source a space to the starboard of the tree.",
            "Situate the oven at one unit of distance to the right of the sylvan being."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.TREE, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_DIAMOND_2_5": {
        "instruction": "Place the furnace five blocks to the top of the diamond",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you position the furnace exactly five blocks above the diamond?",
            "Set the furnace five blocks north from the diamond",
            "Could you set the diamond, then move five blocks up and place the furnace there?",
            "Make sure the furnace is situated five blocks upward from the diamond",
            "Five blocks to the top from the diamond, I want you to put down the furnace"
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.DIAMOND, 2, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PATH_0_1": {
        "instruction": "Please place the stone 1 block to the right of the pathway.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you put the stone exactly one block right next to the path, please?",
            "On the right side of our path, one block away, I need you to position the stone.",
            "Next to our path, but keeping it one block away, and specifically on the right side, can you install the stone there?",
            "Locate the pathway and then go right one block. That's where I'd appreciate if you can place the stone.",
            "Identify the path first. Move one step right from it, and that’s your spot to put the stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PATH, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PATH_2_3": {
        "instruction": "Place furnace 3 blocks to the top of the path.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Three blocks above the path, put a furnace.",
            "Find a path and place a furnace 3 blocks above it.",
            "Go 3 blocks north of a path and there, position a furnace.",
            "On the path, move 3 blocks upwards. There, you should deposit a furnace.",
            "Identify a path and from there, shift three spaces beyond. The location should be perfect for setting up a furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PATH, 2, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PLANT_0_2": {
        "instruction": "Place the stone 2 blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the rock two blocks to the right from the flora.",
            "Establish the stone exactly two squares on the right side of the vegetation.",
            "Set the stone two units towards the right of the herbage.",
            "Arrange the cobble to be two blocks rightward of the shrubbery.",
            "Locate the boulder a couple of blocks on the right-hand side of the greenery."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PLANT, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PLANT_0_3": {
        "instruction": "Place the furnace three blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace to the right of the plant, keeping a distance of three blocks.",
            "On the right side of the plant, maintain a three-block distance and place the furnace there.",
            "Three blocks to the right of the plant, that's where the furnace should be situated.",
            "Establish the location of the furnace three blocks directly right from the plant.",
            "To the exact right of the plant and three blocks away, position the furnace there."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PLANT, 0, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_COAL_1_4": {
        "instruction": "Place the crafting table four blocks to the left of the coal",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench four blocks left from the piece of coal",
            "Position the crafting station a distance of four blocks to the left of the lump of coal",
            "I need you to place the crafting table exactly four squares to the left of the coal block",
            "Could you position the artisan table four segments westwards of the coal deposit?",
            "Make sure you place the crafting table four units to the left of the coal chunk."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.COAL, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_GRASS_3_1": {
        "instruction": "Position a Plant exactly one block below a patch of Grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate a Plant directly one block beneath some Grassland.",
            "Beneath a piece of Turf, place a Plant precisely one block away.",
            "One block downwards from a green Grass area, establish a Plant.",
            "Arrange for a Plant to be exactly one block below a Grass square on the map.",
            "Ensure a Plant is positioned right single block beneath a verdant Grassland."
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.GRASS, 3, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_FURNACE_0_5": {
        "instruction": "Place the Plant 5 blocks to the right of the Furnace",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the right side of the Furnace, position the Plant 5 blocks away",
            "Kindly set the Plant at a distance of 5 blocks to the right from the Furnace",
            "At a gap of 5 blocks to the right from the Furnace, please put down the Plant",
            "Locate the Plant 5 spaces to the right of the Furnace",
            "From the Furnace, travel 5 blocks to the right and there put the Plant"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.FURNACE, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_0_5": {
        "instruction": "Place the crafting table 5 blocks to the right of the water.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Please put the crafting table 5 squares away on the right side of the water.",
            "Could you position the workbench five blocks to the right from the lake, please?",
            "Would you mind setting the bench five to the right of the water?",
            "The crafting table needs to be laid down five blocks to the east of the water.",
            "Can you arrange for the bench to be set five blocks directly right of the water source?"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_1_4": {
        "instruction": "Place the crafting table 4 blocks to the left side of the water",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Set the workbench four slots to the left of the water source",
            "Position the crafting station to the left, exactly four blocks from the water",
            "Situate the crafting table four blocks to the left of the water body",
            "Put the workshop table towards the left, maintaining a distance of four blocks from the water"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_1_2": {
        "instruction": "Place the furnace 2 blocks to the left of the existing furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace two blocks left of the current one.",
            "Position the furnace a gap of two blocks left from the present furnace.",
            "Establish the furnace two blocks leftward from the current furnace.",
            "Put the furnace two blocks to the left side of the furnace already present.",
            "Locate the furnace two blocks towards the left of the old furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 1, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_STONE_3_5": {
        "instruction": "Place the plant five blocks beneath the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Plant the plant five blocks below the rock.",
            "Position the greenery five blocks underneath the boulder.",
            "Put the flora five blocks down from the pebble.",
            "Need you to situate the vegetation five blocks under the cobblestone.",
            "Could you please sit the sapling five blocks downwards from the granite?"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.STONE, 3, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_TREE_0_4": {
        "instruction": "[medium] PLACE PLANT 4 BLOCKS TO THE BOTTOM OF TREE",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "[medium] Plant a seed four squares below the wood.",
            "[medium] Situate a sapling four cells beneath the timber.",
            "[medium] Position foliage four blocks under the hardwood.",
            "[medium] Locate a greens four slots below the log.",
            "[medium] Set the bush fours steps underneath the trunk."
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.TREE, 3, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_GRASS_0_2": {
        "instruction": "Place a stone block 2 squares to the right of the grass block.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "To the right of the grass, keep your stone two blocks away.",
            "2 blocks rightwards from the grass, position your stone.",
            "Situate a stone two cells to the right side of a grass.",
            "Locate a grass. Now, move two spaces to the right and place a stone there.",
            "Put your stone down exactly two patches to the right of any grass."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.GRASS, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_COAL_1_4": {
        "instruction": "Place the crafting table four blocks to the left of the coal",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench four blocks left from the piece of coal",
            "Position the crafting station a distance of four blocks to the left of the lump of coal",
            "I need you to place the crafting table exactly four squares to the left of the coal block",
            "Could you position the artisan table four segments westwards of the coal deposit?",
            "Make sure you place the crafting table four units to the left of the coal chunk."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.COAL, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_GRASS_3_1": {
        "instruction": "Position a Plant exactly one block below a patch of Grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate a Plant directly one block beneath some Grassland.",
            "Beneath a piece of Turf, place a Plant precisely one block away.",
            "One block downwards from a green Grass area, establish a Plant.",
            "Arrange for a Plant to be exactly one block below a Grass square on the map.",
            "Ensure a Plant is positioned right single block beneath a verdant Grassland."
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.GRASS, 3, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_FURNACE_0_5": {
        "instruction": "Place the Plant 5 blocks to the right of the Furnace",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the right side of the Furnace, position the Plant 5 blocks away",
            "Kindly set the Plant at a distance of 5 blocks to the right from the Furnace",
            "At a gap of 5 blocks to the right from the Furnace, please put down the Plant",
            "Locate the Plant 5 spaces to the right of the Furnace",
            "From the Furnace, travel 5 blocks to the right and there put the Plant"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.FURNACE, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_DIAMOND_2_5": {
        "instruction": "Place the furnace five blocks to the top of the diamond",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you position the furnace exactly five blocks above the diamond?",
            "Set the furnace five blocks north from the diamond",
            "Could you set the diamond, then move five blocks up and place the furnace there?",
            "Make sure the furnace is situated five blocks upward from the diamond",
            "Five blocks to the top from the diamond, I want you to put down the furnace"
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.DIAMOND, 2, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PATH_0_1": {
        "instruction": "Please place the stone 1 block to the right of the pathway.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you put the stone exactly one block right next to the path, please?",
            "On the right side of our path, one block away, I need you to position the stone.",
            "Next to our path, but keeping it one block away, and specifically on the right side, can you install the stone there?",
            "Locate the pathway and then go right one block. That's where I'd appreciate if you can place the stone.",
            "Identify the path first. Move one step right from it, and that’s your spot to put the stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PATH, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PATH_2_3": {
        "instruction": "Place furnace 3 blocks to the top of the path.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Three blocks above the path, put a furnace.",
            "Find a path and place a furnace 3 blocks above it.",
            "Go 3 blocks north of a path and there, position a furnace.",
            "On the path, move 3 blocks upwards. There, you should deposit a furnace.",
            "Identify a path and from there, shift three spaces beyond. The location should be perfect for setting up a furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PATH, 2, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PLANT_0_2": {
        "instruction": "Place the stone 2 blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the rock two blocks to the right from the flora.",
            "Establish the stone exactly two squares on the right side of the vegetation.",
            "Set the stone two units towards the right of the herbage.",
            "Arrange the cobble to be two blocks rightward of the shrubbery.",
            "Locate the boulder a couple of blocks on the right-hand side of the greenery."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PLANT, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PLANT_0_3": {
        "instruction": "Place the furnace three blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace to the right of the plant, keeping a distance of three blocks.",
            "On the right side of the plant, maintain a three-block distance and place the furnace there.",
            "Three blocks to the right of the plant, that's where the furnace should be situated.",
            "Establish the location of the furnace three blocks directly right from the plant.",
            "To the exact right of the plant and three blocks away, position the furnace there."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PLANT, 0, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_COAL_1_4": {
        "instruction": "Place the crafting table four blocks to the left of the coal",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench four blocks left from the piece of coal",
            "Position the crafting station a distance of four blocks to the left of the lump of coal",
            "I need you to place the crafting table exactly four squares to the left of the coal block",
            "Could you position the artisan table four segments westwards of the coal deposit?",
            "Make sure you place the crafting table four units to the left of the coal chunk."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.COAL, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_GRASS_3_1": {
        "instruction": "Position a Plant exactly one block below a patch of Grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate a Plant directly one block beneath some Grassland.",
            "Beneath a piece of Turf, place a Plant precisely one block away.",
            "One block downwards from a green Grass area, establish a Plant.",
            "Arrange for a Plant to be exactly one block below a Grass square on the map.",
            "Ensure a Plant is positioned right single block beneath a verdant Grassland."
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.GRASS, 3, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_FURNACE_0_5": {
        "instruction": "Place the Plant 5 blocks to the right of the Furnace",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the right side of the Furnace, position the Plant 5 blocks away",
            "Kindly set the Plant at a distance of 5 blocks to the right from the Furnace",
            "At a gap of 5 blocks to the right from the Furnace, please put down the Plant",
            "Locate the Plant 5 spaces to the right of the Furnace",
            "From the Furnace, travel 5 blocks to the right and there put the Plant"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.FURNACE, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_DIAMOND_2_5": {
        "instruction": "Place the furnace five blocks to the top of the diamond",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you position the furnace exactly five blocks above the diamond?",
            "Set the furnace five blocks north from the diamond",
            "Could you set the diamond, then move five blocks up and place the furnace there?",
            "Make sure the furnace is situated five blocks upward from the diamond",
            "Five blocks to the top from the diamond, I want you to put down the furnace"
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.DIAMOND, 2, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PATH_0_1": {
        "instruction": "Please place the stone 1 block to the right of the pathway.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you put the stone exactly one block right next to the path, please?",
            "On the right side of our path, one block away, I need you to position the stone.",
            "Next to our path, but keeping it one block away, and specifically on the right side, can you install the stone there?",
            "Locate the pathway and then go right one block. That's where I'd appreciate if you can place the stone.",
            "Identify the path first. Move one step right from it, and that’s your spot to put the stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PATH, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PATH_2_3": {
        "instruction": "Place furnace 3 blocks to the top of the path.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Three blocks above the path, put a furnace.",
            "Find a path and place a furnace 3 blocks above it.",
            "Go 3 blocks north of a path and there, position a furnace.",
            "On the path, move 3 blocks upwards. There, you should deposit a furnace.",
            "Identify a path and from there, shift three spaces beyond. The location should be perfect for setting up a furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PATH, 2, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PLANT_0_2": {
        "instruction": "Place the stone 2 blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the rock two blocks to the right from the flora.",
            "Establish the stone exactly two squares on the right side of the vegetation.",
            "Set the stone two units towards the right of the herbage.",
            "Arrange the cobble to be two blocks rightward of the shrubbery.",
            "Locate the boulder a couple of blocks on the right-hand side of the greenery."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PLANT, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PLANT_0_3": {
        "instruction": "Place the furnace three blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace to the right of the plant, keeping a distance of three blocks.",
            "On the right side of the plant, maintain a three-block distance and place the furnace there.",
            "Three blocks to the right of the plant, that's where the furnace should be situated.",
            "Establish the location of the furnace three blocks directly right from the plant.",
            "To the exact right of the plant and three blocks away, position the furnace there."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PLANT, 0, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_COAL_1_4": {
        "instruction": "Place the crafting table four blocks to the left of the coal",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench four blocks left from the piece of coal",
            "Position the crafting station a distance of four blocks to the left of the lump of coal",
            "I need you to place the crafting table exactly four squares to the left of the coal block",
            "Could you position the artisan table four segments westwards of the coal deposit?",
            "Make sure you place the crafting table four units to the left of the coal chunk."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.COAL, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_GRASS_3_1": {
        "instruction": "Position a Plant exactly one block below a patch of Grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate a Plant directly one block beneath some Grassland.",
            "Beneath a piece of Turf, place a Plant precisely one block away.",
            "One block downwards from a green Grass area, establish a Plant.",
            "Arrange for a Plant to be exactly one block below a Grass square on the map.",
            "Ensure a Plant is positioned right single block beneath a verdant Grassland."
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.GRASS, 3, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_FURNACE_0_5": {
        "instruction": "Place the Plant 5 blocks to the right of the Furnace",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the right side of the Furnace, position the Plant 5 blocks away",
            "Kindly set the Plant at a distance of 5 blocks to the right from the Furnace",
            "At a gap of 5 blocks to the right from the Furnace, please put down the Plant",
            "Locate the Plant 5 spaces to the right of the Furnace",
            "From the Furnace, travel 5 blocks to the right and there put the Plant"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.FURNACE, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_0_5": {
        "instruction": "Place the crafting table 5 blocks to the right of the water.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Please put the crafting table 5 squares away on the right side of the water.",
            "Could you position the workbench five blocks to the right from the lake, please?",
            "Would you mind setting the bench five to the right of the water?",
            "The crafting table needs to be laid down five blocks to the east of the water.",
            "Can you arrange for the bench to be set five blocks directly right of the water source?"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_1_4": {
        "instruction": "Place the crafting table 4 blocks to the left side of the water",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Set the workbench four slots to the left of the water source",
            "Position the crafting station to the left, exactly four blocks from the water",
            "Situate the crafting table four blocks to the left of the water body",
            "Put the workshop table towards the left, maintaining a distance of four blocks from the water"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_1_2": {
        "instruction": "Place the furnace 2 blocks to the left of the existing furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace two blocks left of the current one.",
            "Position the furnace a gap of two blocks left from the present furnace.",
            "Establish the furnace two blocks leftward from the current furnace.",
            "Put the furnace two blocks to the left side of the furnace already present.",
            "Locate the furnace two blocks towards the left of the old furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 1, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_STONE_3_5": {
        "instruction": "Place the plant five blocks beneath the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Plant the plant five blocks below the rock.",
            "Position the greenery five blocks underneath the boulder.",
            "Put the flora five blocks down from the pebble.",
            "Need you to situate the vegetation five blocks under the cobblestone.",
            "Could you please sit the sapling five blocks downwards from the granite?"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.STONE, 3, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_TREE_0_2": {
        "instruction": "Place a stone 2 blocks to the right of a tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "To the right of a tree, put a stone two blocks away.",
            "Next to the tree, position a stone two blocks to the right.",
            "Directly two blocks right of a tree, you need to place a stone.",
            "Two square lengths to the right from a tree, set down a stone.",
            "At a distance of two blocks rightwards from the tree, deposit a stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.TREE, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_2_1": {
        "instruction": "Place the furnace 1 block top of another furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace one block above a pre-existing furnace.",
            "Arrange a furnace one block higher than another furnace.",
            "Install a furnace a block above another furnace.",
            "Position a furnace one block ahead on top of another.",
            "Put the furnace one block ahead above another furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_STONE_1_5": {
        "instruction": "Place the crafting table five blocks to the left of the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench five steps left from the rock.",
            "Locate the stone, then place the craftsman's table five blocks to its left.",
            "Situate the carpenter's bench five blocks to the west of the cobblestone.",
            "Find the boulder and install the artisan's flat surface five strides to its port side.",
            "On the offshore side from the pebble, station the joiner's work surface at a distance of five blocks."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.STONE, 1, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_TREE_2_1": {
        "instruction": "Place the crafting table one block to the top of the tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench a block above the tree.",
            "The crafting table should be positioned one block higher than the tree.",
            "Set the workbench one level upward from the tree.",
            "Put the crafting station one block towards the sky from the tree.",
            "Position the workbench above the tree at a distance of a single block."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.TREE, 2, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_TREE_0_1": {
        "instruction": "Place the furnace one block to the right of the tree.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the burner one brick away to the carriage hand of the arboreal structure.",
            "Position the heater precisely one cube to the east of the wooded tract.",
            "Locate the kiln a single stone's distance to the right side of the timber source.",
            "Position the heat source a space to the starboard of the tree.",
            "Situate the oven at one unit of distance to the right of the sylvan being."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.TREE, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_DIAMOND_2_5": {
        "instruction": "Place the furnace five blocks to the top of the diamond",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you position the furnace exactly five blocks above the diamond?",
            "Set the furnace five blocks north from the diamond",
            "Could you set the diamond, then move five blocks up and place the furnace there?",
            "Make sure the furnace is situated five blocks upward from the diamond",
            "Five blocks to the top from the diamond, I want you to put down the furnace"
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.DIAMOND, 2, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PATH_0_1": {
        "instruction": "Please place the stone 1 block to the right of the pathway.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you put the stone exactly one block right next to the path, please?",
            "On the right side of our path, one block away, I need you to position the stone.",
            "Next to our path, but keeping it one block away, and specifically on the right side, can you install the stone there?",
            "Locate the pathway and then go right one block. That's where I'd appreciate if you can place the stone.",
            "Identify the path first. Move one step right from it, and that’s your spot to put the stone."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PATH, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PATH_2_3": {
        "instruction": "Place furnace 3 blocks to the top of the path.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Three blocks above the path, put a furnace.",
            "Find a path and place a furnace 3 blocks above it.",
            "Go 3 blocks north of a path and there, position a furnace.",
            "On the path, move 3 blocks upwards. There, you should deposit a furnace.",
            "Identify a path and from there, shift three spaces beyond. The location should be perfect for setting up a furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PATH, 2, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_PLANT_0_2": {
        "instruction": "Place the stone 2 blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the rock two blocks to the right from the flora.",
            "Establish the stone exactly two squares on the right side of the vegetation.",
            "Set the stone two units towards the right of the herbage.",
            "Arrange the cobble to be two blocks rightward of the shrubbery.",
            "Locate the boulder a couple of blocks on the right-hand side of the greenery."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.PLANT, 0, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PLANT_0_3": {
        "instruction": "Place the furnace three blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace to the right of the plant, keeping a distance of three blocks.",
            "On the right side of the plant, maintain a three-block distance and place the furnace there.",
            "Three blocks to the right of the plant, that's where the furnace should be situated.",
            "Establish the location of the furnace three blocks directly right from the plant.",
            "To the exact right of the plant and three blocks away, position the furnace there."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PLANT, 0, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_COAL_1_4": {
        "instruction": "Place the crafting table four blocks to the left of the coal",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Put the workbench four blocks left from the piece of coal",
            "Position the crafting station a distance of four blocks to the left of the lump of coal",
            "I need you to place the crafting table exactly four squares to the left of the coal block",
            "Could you position the artisan table four segments westwards of the coal deposit?",
            "Make sure you place the crafting table four units to the left of the coal chunk."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.COAL, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_GRASS_3_1": {
        "instruction": "Position a Plant exactly one block below a patch of Grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate a Plant directly one block beneath some Grassland.",
            "Beneath a piece of Turf, place a Plant precisely one block away.",
            "One block downwards from a green Grass area, establish a Plant.",
            "Arrange for a Plant to be exactly one block below a Grass square on the map.",
            "Ensure a Plant is positioned right single block beneath a verdant Grassland."
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.GRASS, 3, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_FURNACE_0_5": {
        "instruction": "Place the Plant 5 blocks to the right of the Furnace",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the right side of the Furnace, position the Plant 5 blocks away",
            "Kindly set the Plant at a distance of 5 blocks to the right from the Furnace",
            "At a gap of 5 blocks to the right from the Furnace, please put down the Plant",
            "Locate the Plant 5 spaces to the right of the Furnace",
            "From the Furnace, travel 5 blocks to the right and there put the Plant"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.FURNACE, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_0_5": {
        "instruction": "Place the crafting table 5 blocks to the right of the water.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Please put the crafting table 5 squares away on the right side of the water.",
            "Could you position the workbench five blocks to the right from the lake, please?",
            "Would you mind setting the bench five to the right of the water?",
            "The crafting table needs to be laid down five blocks to the east of the water.",
            "Can you arrange for the bench to be set five blocks directly right of the water source?"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 0, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_1_4": {
        "instruction": "Place the crafting table 4 blocks to the left side of the water",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Set the workbench four slots to the left of the water source",
            "Position the crafting station to the left, exactly four blocks from the water",
            "Situate the crafting table four blocks to the left of the water body",
            "Put the workshop table towards the left, maintaining a distance of four blocks from the water"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FURNACE_1_2": {
        "instruction": "Place the furnace 2 blocks to the left of the existing furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace two blocks left of the current one.",
            "Position the furnace a gap of two blocks left from the present furnace.",
            "Establish the furnace two blocks leftward from the current furnace.",
            "Put the furnace two blocks to the left side of the furnace already present.",
            "Locate the furnace two blocks towards the left of the old furnace."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FURNACE, 1, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_STONE_3_5": {
        "instruction": "Place the plant five blocks beneath the stone.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Plant the plant five blocks below the rock.",
            "Position the greenery five blocks underneath the boulder.",
            "Put the flora five blocks down from the pebble.",
            "Need you to situate the vegetation five blocks under the cobblestone.",
            "Could you please sit the sapling five blocks downwards from the granite?"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.STONE, 3, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PLANT_0_3": {
        "instruction": "Place the furnace three blocks to the right of the plant.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace to the right of the plant, keeping a distance of three blocks.",
            "On the right side of the plant, maintain a three-block distance and place the furnace there.",
            "Three blocks to the right of the plant, that's where the furnace should be situated.",
            "Establish the location of the furnace three blocks directly right from the plant.",
            "To the exact right of the plant and three blocks away, position the furnace there."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PLANT, 0, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    }
}

hard = {
    "INSTRUCTION_PLACE_STONE_FURNACE_1_2": {
        "instruction": "Place the stone two blocks to the left of the furnace.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Two blocks to the left of the furnace, place the stone.",
            "Locate the furnace, then move two blocks to the left and place the stone.",
            "Starting at the furnace, move two spaces to the left and deposit the stone.",
            "At a two blocks distance leftward from the furnace, install the stone.",
            "Identify the furnace, then shift two blocks to left side and set the stone there."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.FURNACE, 1, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_RUBY_2_2": {
        "instruction": "Place the furnace two blocks above the ruby.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the furnace with two blocks of space directly over the ruby.",
            "Situate the furnace a couple of blocks higher than the ruby.",
            "You should find a ruby and locate the furnace two blocks higher than its position.",
            "Look for a ruby and ensure that a furnace is set two blocks above it.",
            "The furnace needs to be placed in a location that is specifically two blocks higher than the ruby."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.RUBY, 2, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_ENCHANTMENT_TABLE_FIRE_WATER_2_2": {
        "instruction": "Place the Fire Enchantment table two blocks above the water source.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Two blocks above the water source, position a Fire Enchantment table.",
            "Set the Fire Enchantment table up exactly two spots to the top from the water source.",
            "Establish the Fire Enchantment table two blocks upwards from the water point.",
            "Situate the Fire Enchantment table precisely two spaces north from the water body.",
            "The Fire Enchantment table needs to be situated two blocks higher in relation to the point of water."
        ],
        "arguments": create_target_state(BlockType.ENCHANTMENT_TABLE_FIRE, BlockType.WATER, 2, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_RIPE_PLANT_0_4": {
        "instruction": "Place the stone 4 squares to the right side of the ripe plant",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Move the rock to the right side of the ripe plant, making sure it's 4 steps away from it",
            "Ensure the stone is four blocks to the right side of the fully grown plant",
            "Situate the stone four spaces to the right direction from the ripened plant",
            "Put the rock at a distance of four squares towards the right from the matured vegetation",
            "Position the stone four steps in the direction of right from the grown plant"
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.RIPE_PLANT, 0, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FOUNTAIN_0_1": {
        "instruction": "Place a furnace one block to the right of the fountain",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Situate the furnace a single block to the right side of the water feature.",
            "Position the heating unit one square to the right of the fountain.",
            "Orient the furnace to be a unit distance east side of the water fountain.",
            "Locate the furnace one block starboard of the fountain.",
            "Install the furnace a block's space to the eastward direction of the fountain."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FOUNTAIN, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_FIRE_GRASS_1_4": {
        "instruction": "Place the stone four blocks to the left of the fire grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "To the left of fire grass, place the stone four blocks away.",
            "Arrange the stone leftwards from the fire grass, maintaining a distance of four blocks.",
            "Position the stone four blocks towards the left side of the fire grass.",
            "On the left side of the fire grass, station the stone four blocks apart.",
            "Keep the stone four blocks to the west of the fire grass."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.FIRE_GRASS, 1, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_ENCHANTMENT_TABLE_FIRE_TREE_0_1": {
        "instruction": "Place the enchantment table fire one block to the right of the tree",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "On the tree's right side, leave a space of one block, then put the enchantment table fire.",
            "To the immediate right of the tree, the enchantment fire table should be positioned.",
            "Set the enchantment table fire just one block rightward from the tree.",
            "Establish the enchantment table fire exactly a block to the right of the tree.",
            "Situate the enchantment table fire precisely one block right to the tree."
        ],
        "arguments": create_target_state(BlockType.ENCHANTMENT_TABLE_FIRE, BlockType.TREE, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_STONE_FIRE_GRASS_1_3": {
        "instruction": "Put the stone 3 blocks to the left of the fire grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the rock three spaces left from the fire grass.",
            "Place the stone at a distance of three blocks to the left from the fire grass.",
            "From the fire grass, move three steps to the left and put the stone there.",
            "You should locate the stone three blocks away on the left side of the fire grass.",
            "Set the stone in the location three blocks left to the fire grass."
        ],
        "arguments": create_target_state(BlockType.STONE, BlockType.FIRE_GRASS, 1, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_PLANT_0_1": {
        "instruction": "Place the furnace one block to the right of the plant",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Place the oven one block to the plant's right",
            "To the right of the vegetation, position the furnace one block away",
            "Position the kiln a block to the right of the flora",
            "Position the heating device to the right of the plant, leaving a block in between",
            "Set the furnace a block away due east of the plant"
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.PLANT, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_ENCHANTMENT_TABLE_FIRE_2_5": {
        "instruction": "Place a crafting table 5 blocks above the fire enchantment table",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Set the workbench five steps north of fire enhancement block",
            "Identify the fire spell table, then put your crafting desk five blocks on top of it",
            "Five blocks to the top of the fire magic table, place your crafting table",
            "Spot the fire enchantment block, then proceed to install your workstation five blocks above it",
            "Locate the fire spell workbench and situate your crafting table five blocks overhead."
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.ENCHANTMENT_TABLE_FIRE, 2, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_FURNACE_FIRE_GRASS_2_4": {
        "instruction": "Place the furnace four blocks directly above the fire grass.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the furnace on top of the fire grass, leaving a gap of four blocks.",
            "Situate the furnace four blocks overhead of the fire grass.",
            "Erect the furnace four blocks upward from the fire grass.",
            "Install the furnace vertically up to the fire grass, ensuring there's a distance of four blocks.",
            "Arrange for the furnace to be settled four blocks skyward from the fire grass."
        ],
        "arguments": create_target_state(BlockType.FURNACE, BlockType.FIRE_GRASS, 2, 4),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_PLANT_DARKNESS_3_3": {
        "instruction": "Place a plant three blocks below the area of darkness",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position a plant three blocks south of the dark zone",
            "Situate a plant exactly three blocks beneath the shadowy region",
            "Set a plant to the direct downside of the dark realm, three blocks away",
            "Establish a plant's location at a distance of three blocks on the downside of the obscure area",
            "Install a plant at a gap of three blocks underneath the shady territory"
        ],
        "arguments": create_target_state(BlockType.PLANT, BlockType.DARKNESS, 3, 3),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_ENCHANTMENT_TABLE_FIRE_INVALID_3_2": {
        "instruction": "Place the fire enchantment table two blocks below the invalid block",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Aim to put the fire enchanting table exactly two blocks under the invalid block",
            "Ensure the fire enchantment table is situated two blocks beneath the invalid block",
            "You need to position the fire enchantment table two spaces down from the invalid block",
            "Can you put the fire enchantment table two blocks underneath the invalid block?",
            "How about installing the fire enchantment table two blocks straight down from the invalid block?"
        ],
        "arguments": create_target_state(BlockType.ENCHANTMENT_TABLE_FIRE, BlockType.INVALID, 3, 2),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_CRAFTING_TABLE_WATER_0_1": {
        "instruction": "Place Crafting Table right 1 block away from the water body",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Position the workbench exactly one block to the right, adjacent to the water source",
            "Near the water, allocate the manufacturing table a single block towards the right side",
            "Locate the assembly platform to the right, with a single block space from the water",
            "Position the water on your left and then, place the crafting table a block away towards your right",
            "Starting from the water source, measure one block towards your right and put down the crafting table there"
        ],
        "arguments": create_target_state(BlockType.CRAFTING_TABLE, BlockType.WATER, 0, 1),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    },
    "INSTRUCTION_PLACE_ENCHANTMENT_TABLE_ICE_RUBY_3_5": {
        "instruction": "Place the enchantment table of ice five blocks below the ruby.",
        "scenario_checker": Scenarios.LOCALIZATION_PLACE,
        "instruction_paraphrases": [
            "Can you position the ice enchantment station five squares beneath the red crystal?",
            "Could you put the icy spellcasting table five grids down from the crimson gem?",
            "Please set the frosty sorcery workstation five units under the ruby jewel.",
            "Would you mind placing the frozen magic crafting station five blocks southward from the scarlet stone?",
            "Could you kindly draw five units downwards from the ruby treasure and put the glaciated wizardry table there?"
        ],
        "arguments": create_target_state(BlockType.ENCHANTMENT_TABLE_ICE, BlockType.RUBY, 3, 5),
        "str_check_lambda": "place_object_relevant_to(gd, ix)"
    }
}