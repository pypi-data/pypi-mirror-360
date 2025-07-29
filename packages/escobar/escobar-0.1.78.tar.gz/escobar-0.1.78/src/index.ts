import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILayoutRestorer
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ICommandPalette, WidgetTracker } from '@jupyterlab/apputils';
import { ILauncher } from '@jupyterlab/launcher';
import { IMainMenu } from '@jupyterlab/mainmenu';

import { ChatWidget } from './chat';


import { INotebookTracker } from '@jupyterlab/notebook';
import { IDebugger } from '@jupyterlab/debugger';

import { voittaLauncherIcon } from './icons/voitta-icon';


namespace CommandIDs {
  export const create = 'escobar:create-chat';
}

/**
 * Initialization data for the escobar extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'escobar:plugin',
  description: 'AI CHAT EXTENSION',
  autoStart: true,
  optional: [ISettingRegistry, ICommandPalette, ILauncher, IMainMenu, ILayoutRestorer,
    INotebookTracker, IDebugger],
  activate: (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null,
    palette: ICommandPalette | null,
    launcher: ILauncher | null,
    mainMenu: IMainMenu | null,
    restorer: ILayoutRestorer | null,
    notebookTracker: INotebookTracker | null,
    debuggerService: IDebugger | null
  ) => {
    console.log('JupyterLab extension escobar is activated!');






    // Create a widget tracker for Escobar chat instances
    const tracker = new WidgetTracker<ChatWidget>({
      namespace: 'escobar'
    });

    // Add the command to create a new chat widget
    const command = CommandIDs.create;
    app.commands.addCommand(command, {
      label: 'Voitta',
      icon: voittaLauncherIcon,
      execute: () => {
        const widget = new ChatWidget(app,
          settingRegistry || undefined,
          notebookTracker || undefined,
          debuggerService || undefined);

        // Add the widget to the left sidebar
        app.shell.add(widget, 'left', { rank: 900 });

        // Activate the widget
        app.shell.activateById(widget.id);

        console.log('Created chat widget with ID:', widget.id);

        // Add the widget to the tracker
        tracker.add(widget);

        return widget;
      }
    });

    // Add the command to the palette
    if (palette) {
      palette.addItem({
        command,
        category: 'Escobar'
      });
    }

    // Add the command to the launcher
    if (launcher) {
      launcher.add({
        command,
        category: 'Other',
        rank: 1
      });
    }

    // Add the command to the menu on the left
    if (mainMenu || true) {
      mainMenu.helpMenu.addGroup([{ command }], 30);
    }

    // Restore the widgets when the layout is restored
    if (restorer) {
      restorer.restore(tracker, {
        command,
        name: widget => 'escobar-chat',
        args: widget => ({ id: widget.id })
      });
    }

    // Load settings
    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log('escobar settings loaded:', settings.composite);
        })
        .catch(reason => {
          console.error('Failed to load settings for escobar.', reason);
        });
    }
  }
};

export default plugin;
