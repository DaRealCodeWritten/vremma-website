import json
import os
from flask import Blueprint, render_template, redirect, url_for
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ProjectStatus(Enum):
    active = "Active"
    completed = "Completed"
    planned = "Planned"

@dataclass
class Project:
    name: str
    description: str
    status: ProjectStatus
    technologies: List[str]
    github_url: str
    demo_url: Optional[str] = None

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'technologies': self.technologies,
            'github_url': self.github_url,
            'demo_url': self.demo_url
        }

    @classmethod
    def from_dict(cls, data: dict):
        statuses = {
            "ACTIVE": ProjectStatus.active,
            "COMPLETE": ProjectStatus.completed,
            "PLANNED": ProjectStatus.planned
        }
        data["status"] = statuses[data["status"]].name
        return cls(
            **data
        )


project = Blueprint("projects", __name__)


@project.route("/projects")
def project_index():
    path = "./webcfg/projects"
    projects = []
    for file in os.listdir(path):
        with open(path + os.path.sep + file) as prj:
            preparse = json.load(prj)
            projects.append(Project.from_dict(preparse))
    if len(projects) == 0:
        return redirect(url_for("/error", error_code=500))
    return render_template("projects/projects.html", projects=projects)