"""Printer profiles service with pre-configured profiles."""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.models.printer_profile import PrinterProfile, PrinterTechnology, PrinterManufacturer
from app.models.manufacturing_parameters import ManufacturingParameters

logger = structlog.get_logger()


class PrinterProfilesService:
    """Service for managing printer profiles."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize printer profiles service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_profile_by_name(self, name: str) -> Optional[PrinterProfile]:
        """
        Get printer profile by name.

        Args:
            name: Profile name

        Returns:
            Printer profile or None
        """
        result = await self.db.execute(
            select(PrinterProfile).where(PrinterProfile.name == name)
        )
        return result.scalar_one_or_none()

    async def list_profiles(
        self,
        technology: Optional[PrinterTechnology] = None,
        manufacturer: Optional[PrinterManufacturer] = None,
        active_only: bool = True
    ) -> List[PrinterProfile]:
        """
        List printer profiles with optional filtering.

        Args:
            technology: Filter by technology
            manufacturer: Filter by manufacturer
            active_only: Only return active profiles

        Returns:
            List of printer profiles
        """
        query = select(PrinterProfile)

        if technology:
            query = query.where(PrinterProfile.technology == technology)
        if manufacturer:
            query = query.where(PrinterProfile.manufacturer == manufacturer)
        if active_only:
            query = query.where(PrinterProfile.is_active == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def seed_default_profiles(self) -> None:
        """Seed database with default printer profiles."""
        logger.info("seeding_printer_profiles")

        profiles = [
            # FDM Printers - Prusa
            {
                "name": "Prusa i3 MK3S+",
                "manufacturer": PrinterManufacturer.PRUSA,
                "model": "i3 MK3S+",
                "technology": PrinterTechnology.FDM,
                "build_volume_x": 250,
                "build_volume_y": 210,
                "build_volume_z": 210,
                "min_layer_height": 0.05,
                "max_layer_height": 0.35,
                "xy_resolution": 0.05,
                "dimensional_accuracy": 0.1,
                "supported_materials": {
                    "PLA": {"max_temp": 215, "bed_temp": 60},
                    "PETG": {"max_temp": 250, "bed_temp": 85},
                    "ABS": {"max_temp": 255, "bed_temp": 110},
                    "TPU": {"max_temp": 230, "bed_temp": 50}
                },
                "max_nozzle_temp": 300,
                "max_bed_temp": 120,
                "heated_chamber": False,
                "max_print_speed": 200,
                "recommended_print_speed": 60,
                "auto_bed_leveling": True,
                "filament_runout_detection": True,
                "power_loss_recovery": True,
                "multi_material": False,
                "post_processing": {"support_removal": "manual"},
                "compatible_slicers": ["PrusaSlicer", "Cura", "Simplify3D"],
                "is_industrial": False
            },
            # FDM Printers - Bambu Lab
            {
                "name": "Bambu Lab X1 Carbon",
                "manufacturer": PrinterManufacturer.BAMBU_LAB,
                "model": "X1 Carbon",
                "technology": PrinterTechnology.FDM,
                "build_volume_x": 256,
                "build_volume_y": 256,
                "build_volume_z": 256,
                "min_layer_height": 0.08,
                "max_layer_height": 0.28,
                "xy_resolution": 0.05,
                "dimensional_accuracy": 0.08,
                "supported_materials": {
                    "PLA": {"max_temp": 220, "bed_temp": 60},
                    "PETG": {"max_temp": 250, "bed_temp": 80},
                    "ABS": {"max_temp": 270, "bed_temp": 100},
                    "TPU": {"max_temp": 240, "bed_temp": 50},
                    "Nylon": {"max_temp": 280, "bed_temp": 90},
                    "PC": {"max_temp": 280, "bed_temp": 100}
                },
                "max_nozzle_temp": 300,
                "max_bed_temp": 110,
                "heated_chamber": True,
                "max_print_speed": 500,
                "recommended_print_speed": 150,
                "auto_bed_leveling": True,
                "filament_runout_detection": True,
                "power_loss_recovery": True,
                "multi_material": True,
                "post_processing": {"support_removal": "manual"},
                "compatible_slicers": ["Bambu Studio", "PrusaSlicer", "Cura"],
                "is_industrial": False
            },
            # FDM Printers - Creality
            {
                "name": "Creality Ender 3 V2",
                "manufacturer": PrinterManufacturer.CREALITY,
                "model": "Ender 3 V2",
                "technology": PrinterTechnology.FDM,
                "build_volume_x": 220,
                "build_volume_y": 220,
                "build_volume_z": 250,
                "min_layer_height": 0.1,
                "max_layer_height": 0.4,
                "xy_resolution": 0.1,
                "dimensional_accuracy": 0.15,
                "supported_materials": {
                    "PLA": {"max_temp": 200, "bed_temp": 60},
                    "PETG": {"max_temp": 235, "bed_temp": 80},
                    "ABS": {"max_temp": 240, "bed_temp": 100},
                    "TPU": {"max_temp": 220, "bed_temp": 50}
                },
                "max_nozzle_temp": 260,
                "max_bed_temp": 100,
                "heated_chamber": False,
                "max_print_speed": 180,
                "recommended_print_speed": 50,
                "auto_bed_leveling": False,
                "filament_runout_detection": False,
                "power_loss_recovery": False,
                "multi_material": False,
                "post_processing": {"support_removal": "manual"},
                "compatible_slicers": ["Cura", "PrusaSlicer", "Simplify3D"],
                "is_industrial": False
            },
            # SLA Printers - Formlabs
            {
                "name": "Formlabs Form 3+",
                "manufacturer": PrinterManufacturer.FORMLABS,
                "model": "Form 3+",
                "technology": PrinterTechnology.SLA,
                "build_volume_x": 145,
                "build_volume_y": 145,
                "build_volume_z": 185,
                "min_layer_height": 0.025,
                "max_layer_height": 0.1,
                "xy_resolution": 0.025,
                "dimensional_accuracy": 0.05,
                "supported_materials": {
                    "Standard Resin": {"wavelength": "405nm"},
                    "Tough Resin": {"wavelength": "405nm"},
                    "Flexible Resin": {"wavelength": "405nm"},
                    "Castable Resin": {"wavelength": "405nm"},
                    "Dental Resin": {"wavelength": "405nm"}
                },
                "max_nozzle_temp": None,
                "max_bed_temp": 35,
                "heated_chamber": False,
                "max_print_speed": None,
                "recommended_print_speed": None,
                "auto_bed_leveling": True,
                "filament_runout_detection": True,
                "power_loss_recovery": False,
                "multi_material": False,
                "post_processing": {
                    "washing": "IPA bath, 10-20 minutes",
                    "curing": "UV curing, 60°C, 30 minutes",
                    "support_removal": "manual"
                },
                "compatible_slicers": ["PreForm"],
                "is_industrial": False
            },
            # SLA Printers - Elegoo
            {
                "name": "Elegoo Mars 3 Pro",
                "manufacturer": PrinterManufacturer.ELEGOO,
                "model": "Mars 3 Pro",
                "technology": PrinterTechnology.SLA,
                "build_volume_x": 143.43,
                "build_volume_y": 89.6,
                "build_volume_z": 175,
                "min_layer_height": 0.01,
                "max_layer_height": 0.2,
                "xy_resolution": 0.035,
                "dimensional_accuracy": 0.05,
                "supported_materials": {
                    "Standard Resin": {"wavelength": "405nm"},
                    "ABS-Like Resin": {"wavelength": "405nm"},
                    "Water-Washable Resin": {"wavelength": "405nm"},
                    "Plant-Based Resin": {"wavelength": "405nm"}
                },
                "max_nozzle_temp": None,
                "max_bed_temp": None,
                "heated_chamber": False,
                "max_print_speed": None,
                "recommended_print_speed": None,
                "auto_bed_leveling": False,
                "filament_runout_detection": True,
                "power_loss_recovery": False,
                "multi_material": False,
                "post_processing": {
                    "washing": "IPA or water bath, 5-10 minutes",
                    "curing": "UV curing, 5-10 minutes",
                    "support_removal": "manual"
                },
                "compatible_slicers": ["Chitubox", "Lychee Slicer"],
                "is_industrial": False
            },
            # Industrial - Stratasys
            {
                "name": "Stratasys F900",
                "manufacturer": PrinterManufacturer.STRATASYS,
                "model": "F900",
                "technology": PrinterTechnology.FDM,
                "build_volume_x": 914,
                "build_volume_y": 610,
                "build_volume_z": 914,
                "min_layer_height": 0.127,
                "max_layer_height": 0.508,
                "xy_resolution": 0.05,
                "dimensional_accuracy": 0.127,
                "supported_materials": {
                    "ABS-M30": {},
                    "PC-ABS": {},
                    "ULTEM 9085": {},
                    "ULTEM 1010": {},
                    "Nylon 12": {},
                    "ASA": {}
                },
                "max_nozzle_temp": 400,
                "max_bed_temp": 200,
                "heated_chamber": True,
                "max_print_speed": 100,
                "recommended_print_speed": 50,
                "auto_bed_leveling": True,
                "filament_runout_detection": True,
                "power_loss_recovery": True,
                "multi_material": True,
                "post_processing": {"support_removal": "soluble or manual"},
                "compatible_slicers": ["GrabCAD Print", "Insight"],
                "is_industrial": True
            },
            # Industrial - EOS
            {
                "name": "EOS P 396",
                "manufacturer": PrinterManufacturer.EOS,
                "model": "P 396",
                "technology": PrinterTechnology.SLS,
                "build_volume_x": 340,
                "build_volume_y": 340,
                "build_volume_z": 600,
                "min_layer_height": 0.06,
                "max_layer_height": 0.15,
                "xy_resolution": 0.1,
                "dimensional_accuracy": 0.15,
                "supported_materials": {
                    "PA 2200": {"powder"},
                    "PA 1101": {"powder"},
                    "PA 3200 GF": {"powder"},
                    "TPU 1301": {"powder"}
                },
                "max_nozzle_temp": None,
                "max_bed_temp": 180,
                "heated_chamber": True,
                "max_print_speed": None,
                "recommended_print_speed": None,
                "auto_bed_leveling": False,
                "filament_runout_detection": False,
                "power_loss_recovery": True,
                "multi_material": False,
                "post_processing": {
                    "depowdering": "compressed air or bead blasting",
                    "surface_finish": "optional dyeing or vapor smoothing"
                },
                "compatible_slicers": ["EOSPRINT"],
                "is_industrial": True
            }
        ]

        for profile_data in profiles:
            # Check if profile already exists
            existing = await self.get_profile_by_name(profile_data["name"])
            if existing:
                logger.info("printer_profile_exists", name=profile_data["name"])
                continue

            # Create printer profile
            profile = PrinterProfile(**profile_data)
            self.db.add(profile)
            await self.db.flush()

            # Create manufacturing parameters
            mfg_params = ManufacturingParameters(
                printer_profile_id=profile.id,
                wall_thickness=1.2 if profile.technology == PrinterTechnology.FDM else 0.8,
                wall_line_count=2 if profile.technology == PrinterTechnology.FDM else 1,
                top_layers=4,
                bottom_layers=4,
                default_infill_density=20,
                infill_pattern="grid",
                support_type="tree" if profile.manufacturer == PrinterManufacturer.BAMBU_LAB else "normal",
                support_density=15,
                support_z_distance=0.2,
                support_interface_layers=3,
                build_plate_adhesion="skirt",
                print_speed=profile.recommended_print_speed or 50,
                travel_speed=150,
                initial_layer_speed=20,
                infill_speed=80,
                retraction_enabled=True,
                retraction_distance=5.0 if profile.technology == PrinterTechnology.FDM else 0.0,
                retraction_speed=45,
                cooling_enabled=True,
                min_fan_speed=0,
                max_fan_speed=100,
            )
            self.db.add(mfg_params)

        await self.db.commit()
        logger.info("printer_profiles_seeded", count=len(profiles))
