"""
Home Plant Care Management System
A smart solution to help users monitor, manage, and optimize plant care at home.
"""
import datetime
import json
import os
import threading
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import timedelta
class PlantHealth(str, Enum):
    HEALTHY = "Healthy"
    WILTING = "Wilting"
    OVERWATERED = "Overwatered"
    UNDERWATERED = "Underwatered"
    DISEASED = "Diseased"
    DYING = "Dying"

class ReminderType(str, Enum):
    WATERING = "Watering"
    FERTILIZING = "Fertilizing"
    PRUNING = "Pruning"
    HEALTH_CHECK = "Health Check"

class LightNeeds(str, Enum):
    LOW = "Low Light"
    MEDIUM = "Medium Light"
    BRIGHT = "Bright Light"
    DIRECT_SUN = "Direct Sun"

class HumidityNeeds(str, Enum):
    LOW = "Low Humidity (30-40%)"
    MEDIUM = "Medium Humidity (40-60%)"
    HIGH = "High Humidity (60-80%)"

# DATA ACCESS CLASS (Handles database/storage operations)
class PlantDataAccess:
    """Data Access Layer - Handles all file/database operations"""
    def __init__(self, data_file: str = "plant_care_data.json"):
        self.data_file = data_file
        self._lock = threading.Lock()  # Thread safety
        self._load_data()
    def _load_data(self):
        """Load data from JSON file with thread safety"""
        with self._lock:
            if os.path.exists(self.data_file):
                try:
                    with open(self.data_file, 'r') as f:
                        self.data = json.load(f)
                except:
                    self._init_empty_data()
            else:
                self._init_empty_data()

    def _init_empty_data(self):
        self.data = {
            "users": {},
            "plants": {},
            "care_schedules": {},
            "health_logs": [],
            "reminders": [],
            "next_ids": {
                "user": 1,
                "plant": 1,
                "schedule": 1,
                "log": 1,
                "reminder": 1
            }
        }
        self._save_data()

    def _save_data(self):
        """Save data to JSON file with thread safety"""
        with self._lock:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)

    def create_user(self, name: str, email: str) -> int:
        user_id = self.data["next_ids"]["user"]
        self.data["users"][str(user_id)] = {
            "id": user_id,
            "name": name,
            "email": email,
            "created_at": str(datetime.datetime.now())
        }
        self.data["next_ids"]["user"] += 1
        self._save_data()
        return user_id

    def get_user(self, user_id: int) -> Optional[Dict]:
        return self.data["users"].get(str(user_id))

    def get_all_users(self) -> List[Dict]:
        return list(self.data["users"].values())

    def create_plant(self, user_id: int, species: str, light_needs: str,
                     humidity_needs: str, soil_type: str) -> int:
        plant_id = self.data["next_ids"]["plant"]
        self.data["plants"][str(plant_id)] = {
            "id": plant_id,
            "user_id": user_id,
            "species": species,
            "light_needs": light_needs,
            "humidity_needs": humidity_needs,
            "soil_type": soil_type,
            "last_watered": None,
            "last_fertilized": None,
            "last_pruned": None,
            "health_status": PlantHealth.HEALTHY.value,
            "added_date": str(datetime.datetime.now())
        }
        self.data["next_ids"]["plant"] += 1
        self._save_data()
        return plant_id

    def get_plant(self, plant_id: int) -> Optional[Dict]:
        return self.data["plants"].get(str(plant_id))

    def get_user_plants(self, user_id: int) -> List[Dict]:
        return [p for p in self.data["plants"].values() if p["user_id"] == user_id]

    def update_plant_health(self, plant_id: int, health_status: str):
        plant = self.get_plant(plant_id)
        if plant:
            plant["health_status"] = health_status
            self._save_data()

    def update_last_watered(self, plant_id: int):
        plant = self.get_plant(plant_id)
        if plant:
            plant["last_watered"] = str(datetime.datetime.now())
            self._save_data()

    def update_last_fertilized(self, plant_id: int):
        plant = self.get_plant(plant_id)
        if plant:
            plant["last_fertilized"] = str(datetime.datetime.now())
            self._save_data()

    def update_last_pruned(self, plant_id: int):
        plant = self.get_plant(plant_id)
        if plant:
            plant["last_pruned"] = str(datetime.datetime.now())
            self._save_data()
    def create_care_schedule(self, plant_id: int, watering_days: int,
                             fertilizing_days: int, pruning_days: int) -> int:
        schedule_id = self.data["next_ids"]["schedule"]
        self.data["care_schedules"][str(schedule_id)] = {
            "id": schedule_id,
            "plant_id": plant_id,
            "watering_interval_days": watering_days,
            "fertilizing_interval_days": fertilizing_days,
            "pruning_interval_days": pruning_days
        }
        self.data["next_ids"]["schedule"] += 1
        self._save_data()
        return schedule_id
    def get_care_schedule(self, plant_id: int) -> Optional[Dict]:
        for schedule in self.data["care_schedules"].values():
            if schedule["plant_id"] == plant_id:
                return schedule
        return None
    def add_health_log(self, plant_id: int, issue: str, status: str):
        log_id = self.data["next_ids"]["log"]
        self.data["health_logs"].append({
            "id": log_id,
            "plant_id": plant_id,
            "date": str(datetime.datetime.now()),
            "issue": issue,
            "status": status
        })
        self.data["next_ids"]["log"] += 1
        self._save_data()
    def get_plant_health_logs(self, plant_id: int) -> List[Dict]:
        return [log for log in self.data["health_logs"] if log["plant_id"] == plant_id]

    def create_reminder(self, user_id: int, plant_id: int, reminder_type: str,
                        due_date: datetime.datetime) -> int:
        reminder_id = self.data["next_ids"]["reminder"]
        self.data["reminders"].append({
            "id": reminder_id,
            "user_id": user_id,
            "plant_id": plant_id,
            "type": reminder_type,
            "due_date": str(due_date),
            "is_completed": False
        })
        self.data["next_ids"]["reminder"] += 1
        self._save_data()
        return reminder_id
    def get_pending_reminders(self, user_id: int) -> List[Dict]:
        now = datetime.datetime.now()
        pending = []
        for r in self.data["reminders"]:
            if r["user_id"] == user_id and not r["is_completed"]:
                due = datetime.datetime.fromisoformat(r["due_date"])
                if due <= now:
                    pending.append(r)
        return pending
    def mark_reminder_completed(self, reminder_id: int):
        for r in self.data["reminders"]:
            if r["id"] == reminder_id:
                r["is_completed"] = True
                self._save_data()
                return True
        return False

class PlantCareController:
    """Controller - Handles all business logic and user actions"""

    def __init__(self, data_access: PlantDataAccess):
        self.data_access = data_access
        self._current_user_id = None
        self._reminder_thread = None
        self._stop_reminder_thread = False

    #user_managment
    def register_user(self, name: str, email: str) -> int:
        """Register a new user"""
        if not name or not email:
            raise ValueError("Name and email are required")
        user_id = self.data_access.create_user(name, email)
        print(f"✅ User '{name}' registered successfully! (ID: {user_id})")
        return user_id

    def login(self, user_id: int) -> bool:
        """Login a user"""
        user = self.data_access.get_user(user_id)
        if user:
            self._current_user_id = user_id
            print(f"✅ Welcome back, {user['name']}!")
            return True
        else:
            print(f"❌ User with ID {user_id} not found")
            return False

    def get_current_user(self) -> Optional[Dict]:
        return self.data_access.get_user(self._current_user_id) if self._current_user_id else None

    #plant_managment
    def add_plant(self, species: str, light_needs: str, humidity_needs: str, soil_type: str) -> int:
        """Add a new plant for the current user"""
        if not self._current_user_id:
            raise Exception("Please login first")

        plant_id = self.data_access.create_plant(self._current_user_id, species, light_needs, humidity_needs, soil_type )
        self.data_access.create_care_schedule(plant_id, watering_days=3, fertilizing_days=14, pruning_days=30)
        self._create_initial_reminders(plant_id)

        print(f"🌱 Plant '{species}' added to your collection! (ID: {plant_id})")
        return plant_id

    def _create_initial_reminders(self, plant_id: int):
        """Create initial reminders for a new plant"""
        schedule = self.data_access.get_care_schedule(plant_id)
        if schedule:
            now = datetime.datetime.now()
            # Watering reminder (tomorrow)
            self.data_access.create_reminder(
                self._current_user_id, plant_id, ReminderType.WATERING.value,
                now + timedelta(days=1)
            )
            # Fertilizing reminder (in 7 days)
            self.data_access.create_reminder(
                self._current_user_id, plant_id, ReminderType.FERTILIZING.value,
                now + timedelta(days=7)
            )

    def view_my_plants(self):
        """Show all plants of current user"""
        if not self._current_user_id:
            print("❌ Please login first")
            return

        plants = self.data_access.get_user_plants(self._current_user_id)
        if not plants:
            print("🌿 You don't have any plants yet. Add one!")
            return

        print("\n" + "=" * 60)
        print(f"📋 YOUR PLANTS ({len(plants)} total)")
        print("=" * 60)
        for plant in plants:
            schedule = self.data_access.get_care_schedule(plant["id"])
            status_emoji = "✅" if plant["health_status"] == "Healthy" else "⚠️"
            print(f"\n{status_emoji} ID: {plant['id']} | 🌸 {plant['species']}")
            print(f"   💡 Light: {plant['light_needs']}")
            print(f"   💧 Humidity: {plant['humidity_needs']}")
            print(f"   🌱 Soil: {plant['soil_type']}")
            print(f"   ❤️ Health: {plant['health_status']}")
            if schedule:
                print(f"   📅 Water every {schedule['watering_interval_days']} days")

    #careing
    def water_plant(self, plant_id: int) -> bool:
        """Water a specific plant"""
        plant = self.data_access.get_plant(plant_id)
        if not plant or plant["user_id"] != self._current_user_id:
            print("❌ Plant not found or doesn't belong to you")
            return False

        self.data_access.update_last_watered(plant_id)
        #mark_watering_reminder_as_completed
        self._complete_reminder_by_plant_type(plant_id, ReminderType.WATERING.value)
        #create_next_watering_reminder
        self._create_next_reminder(plant_id, ReminderType.WATERING.value)
        print(f"💧 You watered your {plant['species']}! It's happy 🌿")
        return True
    def fertilize_plant(self, plant_id: int) -> bool:
        """Fertilize a specific plant"""
        plant = self.data_access.get_plant(plant_id)
        if not plant or plant["user_id"] != self._current_user_id:
            print("❌ Plant not found or doesn't belong to you")
            return False
        self.data_access.update_last_fertilized(plant_id)
        self._complete_reminder_by_plant_type(plant_id, ReminderType.FERTILIZING.value)
        self._create_next_reminder(plant_id, ReminderType.FERTILIZING.value)
        print(f"🌿 You fertilized your {plant['species']}! It will grow strong 💪")
        return True
    def _complete_reminder_by_plant_type(self, plant_id: int, reminder_type: str):
        """Mark all pending reminders of a type as completed"""
        pending = self.data_access.get_pending_reminders(self._current_user_id)
        for r in pending:
            if r["plant_id"] == plant_id and r["type"] == reminder_type:
                self.data_access.mark_reminder_completed(r["id"])

    def _create_next_reminder(self, plant_id: int, reminder_type: str):
        """Create the next reminder based on care schedule"""
        schedule = self.data_access.get_care_schedule(plant_id)
        if not schedule:
            return
        interval_map = \
            {
            ReminderType.WATERING.value: schedule["watering_interval_days"],
            ReminderType.FERTILIZING.value: schedule["fertilizing_interval_days"],
            ReminderType.PRUNING.value: schedule["pruning_interval_days"]
            }
        days = interval_map.get(reminder_type, 7)
        due_date = datetime.datetime.now() + timedelta(days=days)
        self.data_access.create_reminder(self._current_user_id, plant_id, reminder_type, due_date )
    #health
    def report_health_issue(self, plant_id: int, issue: str):
        """Report a health issue for a plant"""
        plant = self.data_access.get_plant(plant_id)
        if not plant or plant["user_id"] != self._current_user_id:
            print("❌ Plant not found")
            return
        #get recommendation
        recommendation = self._get_health_recommendation(issue)
        self.data_access.add_health_log(plant_id, issue, "Reported")
        print(f"\n🏥 Health issue reported for {plant['species']}: '{issue}'")
        print(f"💡 Recommendation: {recommendation}")
        #healthupdatestatus()
        if "die" in issue.lower() or "dead" in issue.lower():
            self.data_access.update_plant_health(plant_id, PlantHealth.DYING.value)
            print("⚠️ Your plant needs immediate attention!")
    def _get_health_recommendation(self, issue: str) -> str:
        """Intelligent recommendation based on issue"""
        issue_lower = issue.lower()
        if "yellow" in issue_lower or "overwater" in issue_lower:
            return "Stop watering for a few days. Let soil dry out. Check drainage."
        elif "brown" in issue_lower or "dry" in issue_lower or "underwater" in issue_lower:
            return "Water thoroughly. Consider increasing watering frequency."
        elif "pest" in issue_lower or "bug" in issue_lower:
            return "Use neem oil spray. Isolate from other plants."
        elif "droop" in issue_lower or "wilt" in issue_lower:
            return "Check soil moisture. Could be over or under watering."
        else:
            return "Monitor the plant closely. Ensure proper light and humidity."
    #reminder and notifications
    def check_reminders(self):
        """Check and display pending reminders"""
        if not self._current_user_id:
            print("❌ Please login first")
            return
        pending = self.data_access.get_pending_reminders(self._current_user_id)
        if not pending:
            print("✅ No pending reminders! All caught up!")
            return
        print("\n" + "🔔" * 15)
        print("PENDING REMINDERS")
        print("🔔" * 15)
        for reminder in pending:
            plant = self.data_access.get_plant(reminder["plant_id"])
            plant_name = plant["species"] if plant else "Unknown"
            emoji_map = {
                ReminderType.WATERING.value: "💧",
                ReminderType.FERTILIZING.value: "🌿",
                ReminderType.PRUNING.value: "✂️"
            }
            emoji = emoji_map.get(reminder["type"], "🔔")
            print(f"{emoji} {reminder['type']} | {plant_name} | Due: {reminder['due_date']}")
#reminder monitor
    def start_reminder_monitor(self, check_interval_seconds: int = 30):
        """Start a background thread that monitors reminders (Thread-safe)"""
        if self._reminder_thread and self._reminder_thread.is_alive():
            print("⚠️ Reminder monitor already running")
            return
        self._stop_reminder_thread = False
        def monitor():
            # Thread-local storage for security (each thread has its own context)
            thread_local = threading.local()
            thread_local.user_id = self._current_user_id

            print(f"🔄 Reminder monitor started (checks every {check_interval_seconds}s)")

            while not self._stop_reminder_thread:
                try:
                    # Security check: verify user context
                    if thread_local.user_id:
                        pending = self.data_access.get_pending_reminders(thread_local.user_id)
                        if pending:
                            print("\n" + "🔔🔔🔔 REMINDER ALERT 🔔🔔🔔" + "🔔" * len(pending))
                            for r in pending:
                                plant = self.data_access.get_plant(r["plant_id"])
                                if plant:
                                    print(f"⏰ Time to {r['type'].lower()} your {plant['species']}!")
                    time.sleep(check_interval_seconds)
                except Exception as e:
                    # Audit log (in real system, write to file)
                    print(f"[THREAD SAFETY] Monitor error: {e}")
        self._reminder_thread = threading.Thread(target=monitor, daemon=True)
        self._reminder_thread.start()
    def stop_reminder_monitor(self):
        """Stop the background reminder monitor"""
        self._stop_reminder_thread = True
        print("🛑 Reminder monitor stopped")
              #dashboard
    def show_dashboard(self):
        """Show user dashboard with summary"""
        if not self._current_user_id:
            print("❌ Please login first")
            return

        user = self.get_current_user()
        plants = self.data_access.get_user_plants(self._current_user_id)
        pending = self.data_access.get_pending_reminders(self._current_user_id)
        healthy_count = sum(1 for p in plants if p["health_status"] == PlantHealth.HEALTHY.value)
        print("\n" + "🏠" * 20)
        print(f"  DASHBOARD - Welcome {user['name']}!")
        print("🏠" * 20)
        print(f"🌿 Total Plants: {len(plants)}")
        print(f"✅ Healthy Plants: {healthy_count}")
        print(f"🔔 Pending Reminders: {len(pending)}")
        if pending:
            print("\n📋 Quick Actions:")
            for r in pending[:3]:  # Show first 3
                plant = self.data_access.get_plant(r["plant_id"])
                if plant:
                    print(f"   • {r['type']} - {plant['species']}")

#MAIN APPLICATION (CLI Interface)

class PlantCareApp:
    """Main application entry point"""
    def __init__(self):
        self.data_access = PlantDataAccess()
        self.controller = PlantCareController(self.data_access)
    def run(self):
        """Run the main application loop"""
        self.print_welcome()
        while True:
            if not self.controller._current_user_id:
                self.show_login_menu()
            else:
                self.show_main_menu()
    def print_welcome(self):
        print("\n" + "🌱" * 25)
        print("   HOME PLANT CARE MANAGEMENT SYSTEM")
        print("   Keep your plants happy and healthy!")
        print("🌱" * 25)
    def show_login_menu(self):
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("\nChoose: ").strip()
        if choice == "1":
            name = input("Name: ")
            email = input("Email: ")
            try:
                user_id = self.controller.register_user(name, email)
                print(f"\n✨ Your user ID is: {user_id} (save this to login!)")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif choice == "2":
            try:
                user_id = int(input("Enter your User ID: "))
                if self.controller.login(user_id):
                    # Auto-start reminder monitor in background (thread-safe)
                    self.controller.start_reminder_monitor(60)
            except ValueError:
                print("❌ Invalid User ID")

        elif choice == "3":
            print("👋 Goodbye! Keep your plants happy!")
            exit()
    def show_main_menu(self):
        print("\n" + "-" * 40)
        print("🌿 MAIN MENU")
        print("-" * 40)
        print("1. 📋 View My Plants")
        print("2. ➕ Add New Plant")
        print("3. 💧 Water a Plant")
        print("4. 🌿 Fertilize a Plant")
        print("5. 🏥 Report Health Issue")
        print("6. 🔔 Check Reminders")
        print("7. 📊 Dashboard")
        print("8. 🚪 Logout")

        choice = input("\nChoose: ").strip()
        if choice == "1":
            self.controller.view_my_plants()

        elif choice == "2":
            species = input("Plant species (e.g., Monstera, Snake Plant): ")
            print("\nLight needs:")
            print("1. Low Light")
            print("2. Medium Light")
            print("3. Bright Light")
            print("4. Direct Sun")
            light_choice = input("Choose (1-4): ")
            light_map = {"1": "Low Light", "2": "Medium Light", "3": "Bright Light", "4": "Direct Sun"}
            light = light_map.get(light_choice, "Medium Light")

            print("\nHumidity needs:")
            print("1. Low (30-40%)")
            print("2. Medium (40-60%)")
            print("3. High (60-80%)")
            humidity_choice = input("Choose (1-3): ")
            humidity_map = {"1": "Low Humidity (30-40%)", "2": "Medium Humidity (40-60%)",
                            "3": "High Humidity (60-80%)"}
            humidity = humidity_map.get(humidity_choice, "Medium Humidity (40-60%)")

            soil = input("Soil type (e.g., Potting Mix, Cactus Mix): ")

            try:
                self.controller.add_plant(species, light, humidity, soil)
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "3":
            plant_id = int(input("Enter Plant ID to water: "))
            self.controller.water_plant(plant_id)

        elif choice == "4":
            plant_id = int(input("Enter Plant ID to fertilize: "))
            self.controller.fertilize_plant(plant_id)

        elif choice == "5":
            self.controller.view_my_plants()
            plant_id = int(input("\nEnter Plant ID: "))
            issue = input("Describe the issue (e.g., yellow leaves, brown spots, pests): ")
            self.controller.report_health_issue(plant_id, issue)

        elif choice == "6":
            self.controller.check_reminders()

        elif choice == "7":
            self.controller.show_dashboard()

        elif choice == "8":
            self.controller.stop_reminder_monitor()
            self.controller._current_user_id = None
            print("👋 Logged out successfully!")
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    app = PlantCareApp()
    app.run()
