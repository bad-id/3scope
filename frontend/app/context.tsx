import React, { useState } from "react";
import { SystemManager } from "generated";

export const SystemContext = React.createContext<SystemManager | null>(null);
