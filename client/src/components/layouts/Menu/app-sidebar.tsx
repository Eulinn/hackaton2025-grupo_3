import * as React from "react";
import { House, LayoutDashboard, Plus } from "lucide-react";

import { NavMain } from "@/components/layouts/Menu/nav-main";
// import { NavProjects } from "@/components/layouts/Sidebar/nav-projects"
// import { NavUser } from "@/components/layouts/Menu/nav-user";
import { TeamSwitcher } from "@/components/layouts/Menu/team-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";


export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {

  const data = {
    navMain: [
      {
        title: "Home",
        url: "/",
        icon: House,
        isActive: false,
      },
    ],
  };
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        {/* <NavProjects projects={data.projects} /> */}
      </SidebarContent>
      <SidebarFooter>
        {/* <NavUser user={data.user} /> */}
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
